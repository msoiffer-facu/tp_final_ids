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

@views_bp.route("/asistencia")
def asistencia():
    clases = [
        {
            "id": "1",
            "curso": {
                "id":1,
                "nombre":"curso 3b",
                "total_alumnos":40,
                "presentes":10,
            },
            "hora": "15/05/26 15:35",
            "estado":"en_proceso",
        },
        {
            "id": "2",
            "curso": {
                "id":1,
                "nombre":"curso 4a",
                "total_alumnos":25,
                "presentes":10,
            },
            "hora": "14/05/26 21:35",
            "estado":"completado",
        },
        {
            "id": "3",
            "curso": {
                "id":1,
                "nombre":"curso 12c",
                "total_alumnos":30,
            },
            "hora": "14/05/26 13:02",
            "estado":"pendiente",
        },
        {
            "id": "4",
            "curso": {
                "id":1,
                "nombre":"curso 14l",
                "total_alumnos":80,
            },
            "hora": "14/05/26 13:02",
            "estado":"pendiente",
        },
        {
            "id": "5",
            "curso": {
                "id":1,
                "nombre":"curso 1g",
                "total_alumnos":25,
            },
            "hora": "14/05/26 13:02",
            "estado":"pendiente",
        },
    ]
    return render_template("alumnos/asistencia.html", clases=clases)

