from flask import Blueprint, request, jsonify, make_response
from herramientas.generar_pdf import generar_pdf_reporte
from dbs.db_reportes import _fetch_alumnos, _fetch_equipos, _statistics_data

reportes_bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")

PDF_FILENAME = {
    "alumnos": "reporte_alumnos.pdf",
    "estadisticas": "reporte_estadisticas.pdf",
    "equipos": "reporte_equipos.pdf",
}


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

