from flask import Blueprint, render_template, redirect, url_for

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    return redirect(url_for("views.dashboard"))


@views_bp.route("/dashboard")
def dashboard():
    stats = {
        "total_alumnos": 240,
        "total_equipos": 17,
        "prom_asistencia": "88%",
        "notas_subidas": 184,
        "alumnos_promocionados": 46,
    }
    historial = [
        {
            "usuario": "Jose",
            "accion": "Subio las notas pendientes del pr...",
            "area": "Evaluaciones",
            "hora": "15/05/26 15:35",
        },
        {
            "usuario": "Marcos",
            "accion": "Doy de baja a un martin padron 123...",
            "area": "Alumnos",
            "hora": "14/05/26 21:35",
        },
        {
            "usuario": "Martin1",
            "accion": "Subio las notas pendientes del pr...",
            "area": "Evaluaciones",
            "hora": "14/05/26 13:02",
        },
    ]
    return render_template("dashboard.html", stats=stats, historial=historial)
