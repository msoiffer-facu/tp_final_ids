from flask import Blueprint, request, jsonify, make_response
from herramientas.exportar_csv import generar_csv
from herramientas.generar_pdf import generar_pdf_reporte
from dbs.db_reportes import _fetch_alumnos, _fetch_equipos, _statistics_data, _promocionados_por_cuatrimestre

reportes_bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")

PDF_FILENAME = {
    "alumnos": "reporte_alumnos.pdf",
    "estadisticas": "reporte_estadisticas.pdf",
    "equipos": "reporte_equipos.pdf",
}

CSV_FILENAME = {
    "alumnos": "reporte_alumnos.csv",
    "estadisticas": "reporte_estadisticas.csv",
    "equipos": "reporte_equipos.csv",
}

# Mapeo de nombres de columna a etiquetas legibles
_LABELS = {
    "id": "ID",
    "nombre": "Nombre",
    "apellido": "Apellido",
    "dni": "DNI",
    "email": "Email",
    "nota": "Nota",
    "aprobado": "Aprobado",
    "equipo": "Equipo",
    "descripcion": "Descripción",
    "curso": "Curso",
    "miembros": "Miembros",
    "total": "Total",
    "aprobados": "Aprobados",
}


def _human_headers(keys):
    return [_LABELS.get(k, k.replace("_", " ").title()) for k in keys]


def _csv_response(filename, headers, rows):
    csv_data = generar_csv(headers, rows)
    response = make_response(csv_data)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


@reportes_bp.route("/alumnos", methods=["GET"])
def alumnos_listado():
    alumnos = _fetch_alumnos(request.args)
    return jsonify({"data": alumnos, "count": len(alumnos)})


@reportes_bp.route("/alumnos/pdf", methods=["GET"])
def alumnos_pdf():
    alumnos = _fetch_alumnos(request.args)
    if not alumnos:
        return jsonify({"error": "No se encontraron alumnos."}), 404

    keys = list(alumnos[0].keys())
    headers = _human_headers(keys)
    rows = [list(alumno.values()) for alumno in alumnos]
    pdf_bytes = generar_pdf_reporte("Listado de Alumnos", headers, rows)

    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={PDF_FILENAME['alumnos']}"
    return response


@reportes_bp.route("/alumnos/csv", methods=["GET"])
def alumnos_csv():
    alumnos = _fetch_alumnos(request.args)
    if not alumnos:
        return jsonify({"error": "No se encontraron alumnos."}), 404

    keys = list(alumnos[0].keys())
    headers = _human_headers(keys)
    rows = [[alumno.get(key, "") for key in keys] for alumno in alumnos]
    return _csv_response(CSV_FILENAME["alumnos"], headers, rows)


@reportes_bp.route("/equipos", methods=["GET"])
def equipos_listado():
    equipos = _fetch_equipos(request.args)
    return jsonify({"data": equipos, "count": len(equipos)})


@reportes_bp.route("/equipos/pdf", methods=["GET"])
def equipos_pdf():
    equipos = _fetch_equipos(request.args)
    if not equipos:
        return jsonify({"error": "No se encontraron equipos."}), 404

    keys = list(equipos[0].keys())
    headers = _human_headers(keys)
    rows = [list(equipo.values()) for equipo in equipos]
    pdf_bytes = generar_pdf_reporte("Listado de Equipos", headers, rows)

    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={PDF_FILENAME['equipos']}"
    return response


@reportes_bp.route("/equipos/csv", methods=["GET"])
def equipos_csv():
    equipos = _fetch_equipos(request.args)
    if not equipos:
        return jsonify({"error": "No se encontraron equipos."}), 404

    keys = list(equipos[0].keys())
    headers = _human_headers(keys)
    rows = [[equipo.get(key, "") for key in keys] for equipo in equipos]
    return _csv_response(CSV_FILENAME["equipos"], headers, rows)


@reportes_bp.route("/estadisticas", methods=["GET"])
def estadisticas_listado():
    stats = _statistics_data()
    return jsonify(stats)


@reportes_bp.route("/promocionados/cuatrimestre", methods=["GET"])
def promocionados_cuatrimestre():
    data = _promocionados_por_cuatrimestre()
    return jsonify({"data": data, "count": len(data)})


@reportes_bp.route("/estadisticas/pdf", methods=["GET"])
def estadisticas_pdf():
    stats = _statistics_data()
    summary = [
        ("Total de alumnos", stats["total"]),
        ("Aprobados", stats["aprobados"]),
        ("Reprobados", stats["reprobados"]),
        ("Porcentaje de aprobación", f"{stats['porcentaje_aprobacion']} %"),
    ]

    headers = ["Equipo", "Total alumnos", "Aprobados"]
    rows = [[item["equipo"], item["total"], item["aprobados"]] for item in stats["por_equipo"]]
    pdf_bytes = generar_pdf_reporte("Estadísticas de Aprobación", headers, rows, summary)

    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={PDF_FILENAME['estadisticas']}"
    return response


@reportes_bp.route("/estadisticas/csv", methods=["GET"])
def estadisticas_csv():
    stats = _statistics_data()
    rows = [
        ["Resumen", "Total de alumnos", stats["total"]],
        ["Resumen", "Aprobados", stats["aprobados"]],
        ["Resumen", "Reprobados", stats["reprobados"]],
        ["Resumen", "Porcentaje de aprobacion", f"{stats['porcentaje_aprobacion']} %"],
        [],
        ["Por equipo", "Equipo", "Aprobados / total"],
    ]
    rows.extend(
        ["Por equipo", item["equipo"], f"{item['aprobados']} / {item['total']}"]
        for item in stats["por_equipo"]
    )
    return _csv_response(CSV_FILENAME["estadisticas"], ["Seccion", "Metrica", "Valor"], rows)
