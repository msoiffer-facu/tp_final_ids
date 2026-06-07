from flask import Blueprint, render_template, redirect, url_for, request, flash

import services.asistencia as service
from services.curso import obtener_cursos

asistencia_front_bp = Blueprint("asistencia_front", __name__)

@asistencia_front_bp.route("/asistencia", methods=["GET", "POST"])
def asistencia():
    page = int(request.args.get("page", 1))
    per_page = 10
    curso_id = request.args.get("curso", type=int)
    if request.method == "POST":
        curso_id_form = request.form.get("curso")
        try:
            response = service.crear_asistencia(curso_id_form)
        except Exception as e:
            flash(f"Error de conexión al crear la asistencia: {e}", "error")
        return redirect(url_for("asistencia_front.asistencia"))
    cursos = obtener_cursos()
    clases_p = service.obtener_clases_presenciales(page, per_page, curso_id)
    clases_ep = service.obtener_clases_en_proceso()
    if not clases_p:
        clases_p = { "page":0, "total_pages": 0}
        clases = []
    else:
        clases = clases_p['clases_presenciales']

    return render_template(
        "alumnos/asistencia.html",
        clases=clases,
        cursos=cursos,
        curso_id=curso_id,
        page=clases_p["page"],
        total_pages=clases_p["total_pages"],
        clases_en_proceso=clases_ep
    )

@asistencia_front_bp.route("/asistencia/<int:id>")
def asistencia_detalle(id):
    clases = service.obtener_clases_presenciales()['clases_presenciales']
    clase = next((c for c in clases if c["id"] == id), None)
    if not clase:
        return redirect(url_for("asistencia_front.asistencia"))

    alumnos = service.obtener_alumnos_asistencia_clase(id)
    return render_template("alumnos/asistencia_detalle.html", alumnos=alumnos, registro=clase)

@asistencia_front_bp.route("/asistencia/pedir-asistencia", methods=["POST"])
def asistencia_pedir():
        clase_id = request.form.get("asistencia")
        try:
            response = service.pedir_asistencia(clase_id)
        except Exception as e:
            flash(f"Error de conexión al enviar el QR de asistencia: {e}", "error")
        return redirect(url_for("asistencia_front.asistencia"))

@asistencia_front_bp.route("/asistencia/verificar-asistencia", methods=["POST"])
def asistencia_verificar():
        token = request.form.get("token")
        clase_id = request.form.get("asistenciaEscanear")
        finalizar_clase = request.form.get("finalizarClase")
        if not token and finalizar_clase != "true":
            return "Token no enviado", 400

        if not clase_id:
            return "clase no seleccionada", 400

        if finalizar_clase == "true":
            try:
                response = service.finalizar_clase(clase_id)
            except Exception as e:
                flash(f"Error de conexión al finalizar la clase: {e}", "error")
            return redirect(url_for("asistencia_front.asistencia"))

        try:
            response = service.verificar_asistencia(token, clase_id)
        except Exception as e:
            return f"Error interno al conectar con backend: {e}", 500

        return response.text, response.status_code, {"Content-Type": "text/plain; charset=utf-8"}