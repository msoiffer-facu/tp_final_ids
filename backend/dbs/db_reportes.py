from db import get_db
from herramientas.reportes_helpers import (
    normalize_text,
    build_alumno_filters,
    build_equipos_filters,
)


def _table_exists(cursor, table_name):
    cursor.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = %s",
        (table_name,),
    )
    return cursor.fetchone()[0] > 0


def _get_table_columns(cursor, table_name):
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    return [row[0] for row in cursor.fetchall()]


def _fetch_rows(cursor):
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _fetch_alumnos(params):
    conn = get_db()
    try:
        cursor = conn.cursor()
        if not _table_exists(cursor, "alumnos"):
            return []

        columns = _get_table_columns(cursor, "alumnos")
        tiene_equipos = _table_exists(cursor, "equipo_alumnos") and _table_exists(cursor, "equipos")

        select_parts = []
        for col in ["id", "nombre", "apellido", "dni", "email", "nota", "aprobado"]:
            if col in columns:
                select_parts.append(f"a.{col}")

        if not select_parts:
            select_parts = [f"a.{col}" for col in columns]

        if tiene_equipos:
            select_parts.append("IFNULL(e.nombre, 'Sin equipo') AS equipo")

        sql = f"SELECT {', '.join(select_parts)} FROM alumnos a"
        if tiene_equipos:
            sql += (
                " LEFT JOIN equipo_alumnos ea ON ea.alumno_id = a.id"
                " LEFT JOIN equipos e ON e.id = ea.equipo_id"
            )

        filters, values = build_alumno_filters(params, columns, tiene_equipos)
        if filters:
            sql += " WHERE " + " AND ".join(filters)

        sql += " ORDER BY a.apellido, a.nombre"
        cursor.execute(sql, tuple(values))
        alumnos = _fetch_rows(cursor)
        return [{k: normalize_text(v) for k, v in alumno.items()} for alumno in alumnos]
    finally:
        conn.close()


def _fetch_equipos(params):
    conn = get_db()
    try:
        cursor = conn.cursor()
        if not _table_exists(cursor, "equipos"):
            return []

        tiene_cursos = _table_exists(cursor, "cursos")
        tiene_miembros = _table_exists(cursor, "equipo_alumnos")

        sql = "SELECT e.id, e.nombre, e.descripcion"
        if tiene_cursos:
            sql += ", IFNULL(c.nombre, 'Sin curso') AS curso"
        if tiene_miembros:
            sql += ", COUNT(ea.alumno_id) AS miembros"

        sql += " FROM equipos e"
        if tiene_cursos:
            sql += " LEFT JOIN cursos c ON c.id = e.curso_id"
        if tiene_miembros:
            sql += " LEFT JOIN equipo_alumnos ea ON ea.equipo_id = e.id"

        filters, values = build_equipos_filters(params, tiene_cursos)
        if filters:
            sql += " WHERE " + " AND ".join(filters)

        sql += " GROUP BY e.id, e.nombre, e.descripcion"
        if tiene_cursos:
            sql += ", c.nombre"
        sql += " ORDER BY e.nombre"

        cursor.execute(sql, tuple(values))
        equipos = _fetch_rows(cursor)
        return [{k: normalize_text(v) for k, v in equipo.items()} for equipo in equipos]
    finally:
        conn.close()


def _statistics_data():
    conn = get_db()
    try:
        cursor = conn.cursor()
        if not _table_exists(cursor, "alumnos"):
            return {"total": 0, "aprobados": 0, "reprobados": 0, "porcentaje_aprobacion": 0.0, "por_equipo": []}

        columns = _get_table_columns(cursor, "alumnos")
        tiene_equipos = _table_exists(cursor, "equipo_alumnos") and _table_exists(cursor, "equipos")

        if "aprobado" in columns:
            aprobado_expr = "LOWER(CAST(a.aprobado AS CHAR)) IN ('1','true','si','yes','y','s')"
            count_sql = (
                "SELECT COUNT(*) AS total, "
                f"SUM(CASE WHEN {aprobado_expr} THEN 1 ELSE 0 END) AS aprobados, "
                f"SUM(CASE WHEN NOT ({aprobado_expr}) THEN 1 ELSE 0 END) AS reprobados "
                "FROM alumnos a"
            )
        elif "nota" in columns:
            aprobado_expr = "a.nota >= 6"
            count_sql = (
                "SELECT COUNT(*) AS total, "
                "SUM(CASE WHEN a.nota >= 6 THEN 1 ELSE 0 END) AS aprobados, "
                "SUM(CASE WHEN a.nota < 6 OR a.nota IS NULL THEN 1 ELSE 0 END) AS reprobados "
                "FROM alumnos a"
            )
        else:
            cursor.execute("SELECT COUNT(*) AS total FROM alumnos")
            total = cursor.fetchone()[0]
            return {"total": total, "aprobados": 0, "reprobados": 0, "porcentaje_aprobacion": 0.0, "por_equipo": []}

        cursor.execute(count_sql)
        total, aprobados, reprobados = cursor.fetchone()
        total = int(total or 0)
        aprobados = int(aprobados or 0)
        reprobados = int(reprobados or 0)
        porcentaje = round((aprobados / total * 100) if total else 0.0, 2)
        por_equipo = []

        if tiene_equipos:
            cursor.execute(
                f"SELECT IFNULL(e.nombre, 'Sin equipo') AS equipo, "
                f"COUNT(*) AS total, "
                f"SUM(CASE WHEN {aprobado_expr} THEN 1 ELSE 0 END) AS aprobados "
                f"FROM alumnos a "
                f"LEFT JOIN equipo_alumnos ea ON ea.alumno_id = a.id "
                f"LEFT JOIN equipos e ON e.id = ea.equipo_id "
                f"GROUP BY e.id, e.nombre "
                f"ORDER BY total DESC"
            )
            por_equipo = [
                {"equipo": normalize_text(row[0]), "total": int(row[1]), "aprobados": int(row[2] or 0)}
                for row in cursor.fetchall()
            ]

        return {
            "total": total,
            "aprobados": aprobados,
            "reprobados": reprobados,
            "porcentaje_aprobacion": porcentaje,
            "por_equipo": por_equipo,
        }
    finally:
        conn.close()
