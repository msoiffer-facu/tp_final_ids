from db import get_db
from herramientas.reportes_helpers import (
    normalize_text,
    parse_bool,
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
        join_equipos = "equipo_id" in columns and _table_exists(cursor, "equipos")

        select_fields = [f"a.{col}" for col in ["id", "nombre", "apellido", "dni", "email", "nota", "aprobado"] if col in columns]
        if join_equipos:
            select_fields.append("e.nombre AS equipo")

        if not select_fields:
            select_fields = [f"a.{col}" for col in columns]

        sql = f"SELECT {', '.join(select_fields)} FROM alumnos a"
        if join_equipos:
            sql += " LEFT JOIN equipos e ON a.equipo_id = e.id"

        filters, values = build_alumno_filters(params, columns, join_equipos)
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

        columns = _get_table_columns(cursor, "equipos")
        select_fields = [col for col in ["id", "nombre", "tutor", "curso", "turno"] if col in columns]
        if not select_fields:
            select_fields = columns

        sql = f"SELECT {', '.join(select_fields)} FROM equipos"
        filters, values = build_equipos_filters(params, columns)
        if filters:
            sql += " WHERE " + " AND ".join(filters)

        sql += " ORDER BY nombre"
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
        join_equipos = "equipo_id" in columns and _table_exists(cursor, "equipos")

        if "aprobado" in columns:
            count_sql = (
                "SELECT COUNT(*) AS total, "
                "SUM(CASE WHEN LOWER(CAST(aprobado AS CHAR)) IN ('1','true','si','yes','y','s') THEN 1 ELSE 0 END) AS aprobados, "
                "SUM(CASE WHEN LOWER(CAST(aprobado AS CHAR)) NOT IN ('1','true','si','yes','y','s') THEN 1 ELSE 0 END) AS reprobados "
                "FROM alumnos"
            )
        elif "nota" in columns:
            count_sql = (
                "SELECT COUNT(*) AS total, "
                "SUM(CASE WHEN nota >= 6 THEN 1 ELSE 0 END) AS aprobados, "
                "SUM(CASE WHEN nota < 6 THEN 1 ELSE 0 END) AS reprobados "
                "FROM alumnos"
            )
        else:
            cursor.execute("SELECT COUNT(*) AS total FROM alumnos")
            total = cursor.fetchone()[0]
            return {"total": total, "aprobados": 0, "reprobados": 0, "porcentaje_aprobacion": 0.0, "por_equipo": []}

        cursor.execute(count_sql)
        total, aprobados, reprobados = cursor.fetchone()
        porcentaje = round((aprobados / total * 100) if total else 0.0, 2)
        por_equipo = []

        if join_equipos:
            cursor.execute(
                "SELECT IFNULL(e.nombre, 'Sin equipo') AS equipo, "
                "COUNT(*) AS total, "
                "SUM(CASE WHEN LOWER(CAST(a.aprobado AS CHAR)) IN ('1','true','si','yes','y','s') THEN 1 ELSE 0 END) AS aprobados "
                "FROM alumnos a "
                "LEFT JOIN equipos e ON a.equipo_id = e.id "
                "GROUP BY equipo "
                "ORDER BY total DESC"
            )
            por_equipo = [
                {"equipo": normalize_text(row[0]), "total": int(row[1]), "aprobados": int(row[2])}
                for row in cursor.fetchall()
            ]

        return {
            "total": int(total),
            "aprobados": int(aprobados),
            "reprobados": int(reprobados),
            "porcentaje_aprobacion": porcentaje,
            "por_equipo": por_equipo,
        }
    finally:
        conn.close()
