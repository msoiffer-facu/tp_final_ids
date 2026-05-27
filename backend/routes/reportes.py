from flask import Blueprint, request, jsonify, make_response
from db import get_db
from herramientas.generar_pdf import generar_pdf_reporte

reportes_bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")

PDF_FILENAME = {
    "alumnos": "reporte_alumnos.pdf",
    "estadisticas": "reporte_estadisticas.pdf",
    "equipos": "reporte_equipos.pdf",
}


def _normalize_text(value):
    if value is None:
        return ""
    return str(value)


def _parse_bool(value):
    if value is None:
        return None
    value = str(value).strip().lower()
    if value in {"1", "true", "si", "yes", "y", "s"}:
        return True
    if value in {"0", "false", "no", "n"}:
        return False
    return None


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


def _build_alumno_filters(params, columns, join_equipos):
    filters = []
    values = []

    nombre = params.get("nombre")
    apellido = params.get("apellido")
    equipo = params.get("equipo")
    aprobado = _parse_bool(params.get("aprobado"))

    if nombre and "nombre" in columns:
        filters.append("LOWER(a.nombre) LIKE %s")
        values.append(f"%{nombre.lower()}%")
    if apellido and "apellido" in columns:
        filters.append("LOWER(a.apellido) LIKE %s")
        values.append(f"%{apellido.lower()}%")
    if equipo and join_equipos:
        filters.append("LOWER(e.nombre) LIKE %s")
        values.append(f"%{equipo.lower()}%")
    if aprobado is not None and "aprobado" in columns:
        if aprobado:
            filters.append("LOWER(CAST(a.aprobado AS CHAR)) IN ('1','true','si','yes','y','s')")
        else:
            filters.append("LOWER(CAST(a.aprobado AS CHAR)) NOT IN ('1','true','si','yes','y','s')")

    return filters, values


def _build_equipos_filters(params, columns):
    filters = []
    values = []

    nombre = params.get("nombre")
    tutor = params.get("tutor")

    if nombre and "nombre" in columns:
        filters.append("LOWER(nombre) LIKE %s")
        values.append(f"%{nombre.lower()}%")
    if tutor and "tutor" in columns:
        filters.append("LOWER(tutor) LIKE %s")
        values.append(f"%{tutor.lower()}%")

    return filters, values


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

        filters, values = _build_alumno_filters(params, columns, join_equipos)
        if filters:
            sql += " WHERE " + " AND ".join(filters)

        sql += " ORDER BY a.apellido, a.nombre"
        cursor.execute(sql, tuple(values))
        alumnos = _fetch_rows(cursor)
        return [{k: _normalize_text(v) for k, v in alumno.items()} for alumno in alumnos]
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
        filters, values = _build_equipos_filters(params, columns)
        if filters:
            sql += " WHERE " + " AND ".join(filters)

        sql += " ORDER BY nombre"
        cursor.execute(sql, tuple(values))
        equipos = _fetch_rows(cursor)
        return [{k: _normalize_text(v) for k, v in equipo.items()} for equipo in equipos]
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
                {"equipo": _normalize_text(row[0]), "total": int(row[1]), "aprobados": int(row[2])}
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


@reportes_bp.route("/alumnos", methods=["GET"])
def alumnos_listado():
    alumnos = _fetch_alumnos(request.args)
    return jsonify({"data": alumnos, "count": len(alumnos)})


@reportes_bp.route("/alumnos/pdf", methods=["GET"])
def alumnos_pdf():
    alumnos = _fetch_alumnos(request.args)
    if not alumnos:
        return jsonify({"error": "No se encontraron alumnos."}), 404

    title = "Listado de Alumnos"
    headers = list(alumnos[0].keys())
    rows = [list(alumno.values()) for alumno in alumnos]
    pdf_bytes = generar_pdf_reporte(title, headers, rows)

    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={PDF_FILENAME['alumnos']}"
    return response


@reportes_bp.route("/equipos", methods=["GET"])
def equipos_listado():
    equipos = _fetch_equipos(request.args)
    return jsonify({"data": equipos, "count": len(equipos)})


@reportes_bp.route("/equipos/pdf", methods=["GET"])
def equipos_pdf():
    equipos = _fetch_equipos(request.args)
    if not equipos:
        return jsonify({"error": "No se encontraron equipos."}), 404

    title = "Listado de Equipos"
    headers = list(equipos[0].keys())
    rows = [list(equipo.values()) for equipo in equipos]
    pdf_bytes = generar_pdf_reporte(title, headers, rows)

    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={PDF_FILENAME['equipos']}"
    return response


@reportes_bp.route("/estadisticas", methods=["GET"])
def estadisticas_listado():
    stats = _statistics_data()
    return jsonify(stats)


@reportes_bp.route("/estadisticas/pdf", methods=["GET"])
def estadisticas_pdf():
    stats = _statistics_data()
    summary = [
        ("Total de alumnos", stats["total"]),
        ("Aprobados", stats["aprobados"]),
        ("Reprobados", stats["reprobados"]),
        ("Porcentaje de aprobación", f"{stats['porcentaje_aprobacion']} %"),
    ]

    headers = ["Equipo", "Total", "Aprobados"]
    rows = [[item["equipo"], item["total"], item["aprobados"]] for item in stats["por_equipo"]]
    pdf_bytes = generar_pdf_reporte("Estadísticas de aprobación", headers, rows, summary)

    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={PDF_FILENAME['estadisticas']}"
    return response
