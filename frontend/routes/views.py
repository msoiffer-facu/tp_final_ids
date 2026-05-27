from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from services.asistencia import obtener_clases_presenciales , calcular_clases_mes
from services.curso import obtener_cursos
from services.login import usuario_logueado, limpiar_sesion, guardar_sesion

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def home():
    if usuario_logueado():
        return redirect(url_for("views.dashboard"))
    return redirect(url_for("views.login"))


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
    cursos = obtener_cursos()
    clases = obtener_clases_presenciales()
    clasesMes = calcular_clases_mes(clases)
    return render_template("alumnos/asistencia.html", clases=clases,cursos=cursos, clasesMes=clasesMes)

@views_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == "a@test.com" and password == "1234":
            session["user"] = {
                "email": email,
                "name": "Martin"
            }
            session["token"] = "prueba"

            guardar_sesion(session["token"], session["user"])
            flash(f"¡Bienvenido, {session["user"]["name"]}!", "success")
            return redirect(url_for("views.dashboard"))

    return render_template("login.html")

@views_bp.route("/logout", methods=['POST'])
def logout():
    limpiar_sesion()
    flash('Cerraste sesión.', 'success')
    return redirect(url_for("views.login"))
