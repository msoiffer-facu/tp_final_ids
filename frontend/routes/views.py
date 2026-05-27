from flask import Blueprint, render_template, redirect, url_for, abort, request, flash

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


@views_bp.route("/equipos")
def equipos():
    equipos = [
        {
            "id": 1,
            "nombre": "Equipo A",
            "descripcion": "Avance en proyecto final.",
            "estado": "Activo",
            "miembros": 3,
            "curso": "IDS 2026",
        },
        {
            "id": 2,
            "nombre": "Equipo B",
            "descripcion": "En proceso de integración.",
            "estado": "Desconectados",
            "miembros": 2,
            "curso": "IDS 2026",
        },
        {
            "id": 3,
            "nombre": "Equipo C",
            "descripcion": "Necesita completar tareas.",
            "estado": "Incompleto",
            "miembros": 4,
            "curso": "IDS 2026",
        },
    ]

    return render_template("equipos/listado.html", equipos=equipos)


@views_bp.route("/equipos/<int:equipo_id>", methods=["GET", "POST"])
def equipo_detalle(equipo_id):
    equipos = [
        {
            "id": 1,
            "nombre": "Equipo A",
            "descripcion": "Avance en proyecto final.",
            "estado": "Activo",
            "miembros": 3,
            "curso": "IDS 2026",
            "fecha_creacion": "10/05/2026",
        },
        {
            "id": 2,
            "nombre": "Equipo B",
            "descripcion": "En proceso de integración.",
            "estado": "Desconectados",
            "miembros": 2,
            "curso": "IDS 2026",
            "fecha_creacion": "12/05/2026",
        },
        {
            "id": 3,
            "nombre": "Equipo C",
            "descripcion": "Necesita completar tareas.",
            "estado": "Incompleto",
            "miembros": 4,
            "curso": "IDS 2026",
            "fecha_creacion": "16/05/2026",
        },
    ]

    equipo = next((item for item in equipos if item["id"] == equipo_id), None)
    if not equipo:
        return abort(404)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            flash("Equipo eliminado correctamente.", "success")
            return redirect(url_for("views.equipos"))
        flash("Datos del equipo actualizados.", "success")
        return redirect(url_for("views.equipo_detalle", equipo_id=equipo_id))

    miembros = [
        {"padron": "12345", "nombre": "Luca", "apellido": "Perez"},
        {"padron": "12346", "nombre": "Ana", "apellido": "Gomez"},
        {"padron": "12347", "nombre": "Mica", "apellido": "Lopez"},
    ]

    return render_template("equipos/abm.html", equipo=equipo, miembros=miembros)
