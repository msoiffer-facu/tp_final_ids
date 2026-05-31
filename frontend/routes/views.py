from flask import Blueprint, render_template, redirect, url_for, request, session, flash
import requests
from services.asistencia import obtener_clases_presenciales , calcular_clases_mes
from services.curso import obtener_cursos
from services.login import usuario_logueado, limpiar_sesion, guardar_sesion

views_bp = Blueprint("views", __name__)

@views_bp.route("/")
def index():
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
        {"usuario": "Jose", "accion": "Subio las notas pendientes del pr...", "area": "Evaluaciones", "hora": "15/05/26 15:35"},
        {"usuario": "Marcos", "accion": "Doy de baja a un martin padron 123...", "area": "Alumnos", "hora": "14/05/26 21:35"},
        {"usuario": "Martin1", "accion": "Subio las notas pendientes del pr...", "area": "Evaluaciones", "hora": "14/05/26 13:02"},
    ]
    return render_template("dashboard.html", stats=stats, historial=historial)


@views_bp.route("/cursos")
def cursos():
    try:
        response = requests.get("http://localhost:5000/cursos/cursos")
        cursos = response.json()
    except:
        cursos = []
    return render_template("cursos/cursos.html", cursos=cursos)


@views_bp.route("/cursos/<int:id>")
def curso_detalle(id):
    try:
        curso = requests.get(f"http://localhost:5000/cursos/cursos/{id}").json()
        alumnos = requests.get(f"http://localhost:5000/cursos/cursos/{id}/alumnos").json()
        equipos = requests.get(f"http://localhost:5000/cursos/cursos/{id}/equipos").json()
        clases = requests.get(f"http://localhost:5000/cursos/cursos/{id}/clases").json()
    except:
        return redirect(url_for("views.cursos"))
    return render_template("cursos/curso_detalle.html", curso=curso, alumnos=alumnos, equipos=equipos, clases=clases)


@views_bp.route("/cursos/nuevo", methods=["GET", "POST"])
def curso_nuevo():
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "cuatrimestre": request.form.get("cuatrimestre"),
            "anio": int(request.form.get("anio")),
            "modificacion": request.form.get("modificacion")
        }
        requests.post("http://localhost:5000/cursos/cursos", json=data)
        return redirect(url_for("views.cursos"))
    return render_template("cursos/curso_form.html", curso=None)


@views_bp.route("/cursos/<int:id>/editar", methods=["GET", "POST"])
def curso_editar(id):
    try:
        curso = requests.get(f"http://localhost:5000/cursos/cursos/{id}").json()
    except:
        return redirect(url_for("views.cursos"))
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "cuatrimestre": request.form.get("cuatrimestre"),
            "anio": int(request.form.get("anio")),
            "modificacion": request.form.get("modificacion")
        }
        requests.put(f"http://localhost:5000/cursos/cursos/{id}", json=data)
        return redirect(url_for("views.curso_detalle", id=id))
    return render_template("cursos/curso_form.html", curso=curso)


@views_bp.route("/cursos/<int:id>/eliminar", methods=["POST"])
def curso_eliminar(id):
    requests.delete(f"http://localhost:5000/cursos/cursos/{id}")
    return redirect(url_for("views.cursos"))

@views_bp.route("/profesores")
def profesores():
    return render_template("profesores/profesores.html", profesores=PROFESORES)


@views_bp.route("/profesores/nuevo", methods=["GET", "POST"])
def profesor_nuevo():
    if request.method == "POST":
        nuevo = {
            "id": len(PROFESORES) + 1,
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "email": request.form.get("email"),
            "telefono": request.form.get("telefono"),
            "asignatura": request.form.get("asignatura"),
            "estado": request.form.get("estado", "Inactivo"),
        }
        PROFESORES.append(nuevo)
        return redirect(url_for("views.profesores"))
    return render_template("profesores/profesor_form.html", profesor=None)


@views_bp.route("/profesores/<int:id>")
def profesor_detalle(id):
    profesor = next((p for p in PROFESORES if p["id"] == id), None)
    if not profesor:
        return redirect(url_for("views.profesores"))
    return render_template("profesores/profesor_detalle.html", profesor=profesor)


@views_bp.route("/profesores/<int:id>/editar", methods=["GET", "POST"])
def profesor_editar(id):
    profesor = next((p for p in PROFESORES if p["id"] == id), None)
    if not profesor:
        return redirect(url_for("views.profesores"))
    if request.method == "POST":
        profesor["nombre"] = request.form.get("nombre")
        profesor["apellido"] = request.form.get("apellido")
        profesor["email"] = request.form.get("email")
        profesor["telefono"] = request.form.get("telefono")
        profesor["asignatura"] = request.form.get("asignatura")
        profesor["estado"] = request.form.get("estado", "Inactivo")
        return redirect(url_for("views.profesor_detalle", id=id))
    return render_template("profesores/profesor_form.html", profesor=profesor)


@views_bp.route("/profesores/<int:id>/eliminar", methods=["POST"])
def profesor_eliminar(id):
    global PROFESORES
    PROFESORES = [p for p in PROFESORES if p["id"] != id]
    return redirect(url_for("views.profesores"))


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
