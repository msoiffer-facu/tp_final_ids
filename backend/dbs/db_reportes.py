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
        tiene_notas = _table_exists(cursor, "notas")
        tiene_equipos = _table_exists(cursor, "equipo_alumnos") and _table_exists(cursor, "equipos")

        cursor.execute("SELECT COUNT(*) FROM alumnos")
        total = int(cursor.fetchone()[0] or 0)

        if tiene_notas:
            aprobado_estados = "('APROBADO', 'PROMOCIONADO')"
            cursor.execute(
                "SELECT "
                f"COUNT(DISTINCT CASE WHEN n.estado IN {aprobado_estados} THEN n.alumno_id END) AS aprobados, "
                "COUNT(DISTINCT CASE WHEN n.estado = 'DESAPROBADO' THEN n.alumno_id END) AS reprobados "
                "FROM notas n"
            )
            aprobados, reprobados = cursor.fetchone()
            aprobados = int(aprobados or 0)
            reprobados = int(reprobados or 0)
        elif "aprobado" in columns:
            aprobado_expr = "LOWER(CAST(a.aprobado AS CHAR)) IN ('1','true','si','yes','y','s')"
            cursor.execute(
                "SELECT "
                f"SUM(CASE WHEN {aprobado_expr} THEN 1 ELSE 0 END) AS aprobados, "
                f"SUM(CASE WHEN NOT ({aprobado_expr}) THEN 1 ELSE 0 END) AS reprobados "
                "FROM alumnos a"
            )
            aprobados, reprobados = cursor.fetchone()
            aprobados = int(aprobados or 0)
            reprobados = int(reprobados or 0)
        elif "nota" in columns:
            cursor.execute(
                "SELECT "
                "SUM(CASE WHEN a.nota >= 6 THEN 1 ELSE 0 END) AS aprobados, "
                "SUM(CASE WHEN a.nota < 6 OR a.nota IS NULL THEN 1 ELSE 0 END) AS reprobados "
                "FROM alumnos a"
            )
            aprobados, reprobados = cursor.fetchone()
            aprobados = int(aprobados or 0)
            reprobados = int(reprobados or 0)
        else:
            aprobados = 0
            reprobados = 0

        porcentaje = round((aprobados / total * 100) if total else 0.0, 2)
        por_equipo = []

        if tiene_equipos and tiene_notas:
            aprobado_estados = "('APROBADO', 'PROMOCIONADO')"
            cursor.execute(
                "SELECT IFNULL(e.nombre, 'Sin equipo') AS equipo, "
                "COUNT(DISTINCT ea.alumno_id) AS total, "
                f"COUNT(DISTINCT CASE WHEN n.estado IN {aprobado_estados} THEN n.alumno_id END) AS aprobados "
                "FROM equipo_alumnos ea "
                "LEFT JOIN equipos e ON e.id = ea.equipo_id "
                "LEFT JOIN notas n ON n.alumno_id = ea.alumno_id "
                "GROUP BY e.id, e.nombre "
                "ORDER BY total DESC"
            )
            por_equipo = [
                {"equipo": normalize_text(row[0]), "total": int(row[1]), "aprobados": int(row[2] or 0)}
                for row in cursor.fetchall()
            ]
        elif tiene_equipos and "aprobado" in columns:
            aprobado_expr = "LOWER(CAST(a.aprobado AS CHAR)) IN ('1','true','si','yes','y','s')"
            cursor.execute(
                "SELECT IFNULL(e.nombre, 'Sin equipo') AS equipo, "
                "COUNT(*) AS total, "
                f"SUM(CASE WHEN {aprobado_expr} THEN 1 ELSE 0 END) AS aprobados "
                "FROM alumnos a "
                "LEFT JOIN equipo_alumnos ea ON ea.alumno_id = a.id "
                "LEFT JOIN equipos e ON e.id = ea.equipo_id "
                "GROUP BY e.id, e.nombre "
                "ORDER BY total DESC"
            )
            por_equipo = [
                {"equipo": normalize_text(row[0]), "total": int(row[1]), "aprobados": int(row[2] or 0)}
                for row in cursor.fetchall()
            ]
        elif tiene_equipos and "nota" in columns:
            cursor.execute(
                "SELECT IFNULL(e.nombre, 'Sin equipo') AS equipo, "
                "COUNT(*) AS total, "
                "SUM(CASE WHEN a.nota >= 6 THEN 1 ELSE 0 END) AS aprobados "
                "FROM alumnos a "
                "LEFT JOIN equipo_alumnos ea ON ea.alumno_id = a.id "
                "LEFT JOIN equipos e ON e.id = ea.equipo_id "
                "GROUP BY e.id, e.nombre "
                "ORDER BY total DESC"
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


def _promocionados_por_cuatrimestre():
    conn = get_db()
    try:
        cursor = conn.cursor()
        required_tables = ["cursos", "alumnos_curso", "evaluaciones", "notas"]
        if any(not _table_exists(cursor, table) for table in required_tables):
            return []

        cursor.execute(
            """
            SELECT
                c.id,
                c.nombre,
                c.anio,
                c.cuatrimestre,
                COUNT(DISTINCT ac.alumnos_id) AS total_alumnos,
                COUNT(DISTINCT CASE
                    WHEN n.estado = 'PROMOCIONADO' THEN n.alumno_id
                    ELSE NULL
                END) AS promocionados
            FROM cursos c
            LEFT JOIN alumnos_curso ac
                ON ac.curso_id = c.id
            LEFT JOIN evaluaciones e
                ON e.curso_id = c.id
            LEFT JOIN notas n
                ON n.evaluacion_id = e.id
                AND n.alumno_id = ac.alumnos_id
            GROUP BY c.id, c.nombre, c.anio, c.cuatrimestre
            ORDER BY c.anio, c.cuatrimestre, c.nombre
            """
        )

        por_periodo = {}
        for curso_id, nombre, anio, cuatrimestre, total, promocionados in cursor.fetchall():
            if anio is None or cuatrimestre is None:
                continue

            periodo = f"{anio}-C{cuatrimestre}"
            total = int(total or 0)
            promocionados = int(promocionados or 0)
            porcentaje = round((promocionados / total * 100) if total else 0, 2)

            if periodo not in por_periodo:
                por_periodo[periodo] = {
                    "periodo": periodo,
                    "total_alumnos": 0,
                    "promocionados": 0,
                    "cursos": [],
                }

            por_periodo[periodo]["total_alumnos"] += total
            por_periodo[periodo]["promocionados"] += promocionados
            por_periodo[periodo]["cursos"].append({
                "id": curso_id,
                "nombre": normalize_text(nombre),
                "total_alumnos": total,
                "promocionados": promocionados,
                "porcentaje": porcentaje,
            })

        resultado = []
        for item in por_periodo.values():
            total = item["total_alumnos"]
            promocionados = item["promocionados"]
            item["promedio"] = round((promocionados / total * 100) if total else 0, 2)
            resultado.append(item)

        return resultado
    finally:
        conn.close()
