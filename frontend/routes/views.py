
from flask import Blueprint, render_template, redirect, url_for, request, abort, flash

from flask import Blueprint, render_template, redirect, url_for, request, session, flash
import requests
from services.asistencia import obtener_clases_presenciales , calcular_clases_mes
from services.curso import obtener_cursos
from services.login import usuario_logueado, limpiar_sesion, guardar_sesion


views_bp = Blueprint("views", __name__)

# Datos hardcodeados para probar
CURSOS = [
    {"id": 1, "nombre": "Introducción al Desarrollo de Software", "anio": 2025, "cuatrimestre": "1", "cantidad_alumnos": 30, "modificacion": "ninguna"},
    {"id": 2, "nombre": "Bases de Datos", "anio": 2025, "cuatrimestre": "2", "cantidad_alumnos": 25, "modificacion": "ninguna"},
]

ALUMNOS = [
    {"id": 1, "padron": 12345, "nombre": "Juan", "apellido": "Perez", "email": "juan@mail.com", "abandono": True, "estado": False},
    {"id": 2, "padron": 67890, "nombre": "Maria", "apellido": "Garcia", "email": "maria@mail.com", "abandono": False, "estado": True},
]

PROFESORES = [
    {"id": 1, "nombre": "Lucia", "apellido": "Martinez", "email": "lucia.martinez@mail.com", "telefono": "+54 11 4567-8901", "asignatura": "Programación", "estado": "Activo"},
    {"id": 2, "nombre": "Carlos", "apellido": "Giordano", "email": "carlos.giordano@mail.com", "telefono": "+54 11 4123-4567", "asignatura": "Bases de Datos", "estado": "Activo"},
    {"id": 3, "nombre": "Veronica", "apellido": "Rossi", "email": "veronica.rossi@mail.com", "telefono": "+54 11 4789-1234", "asignatura": "Arquitectura de Software", "estado": "Inactivo"},
]

EQUIPOS = [
    {"id": 1, "nombre": "Equipo A", "descripcion": "Avance en proyecto final.", "estado": "Activo", "miembros": 3, "curso": "IDS 2026", "fecha_creacion": "10/05/2026"},
    {"id": 2, "nombre": "Equipo B", "descripcion": "En proceso de integración.", "estado": "Desconectados", "miembros": 2, "curso": "IDS 2026", "fecha_creacion": "12/05/2026"},
    {"id": 3, "nombre": "Equipo C", "descripcion": "Necesita completar tareas.", "estado": "Incompleto", "miembros": 4, "curso": "IDS 2026", "fecha_creacion": "16/05/2026"},
]

def get_equipo(equipo_id):
    return next((item for item in EQUIPOS if item["id"] == equipo_id), None)


def next_equipo_id():
    return max((item["id"] for item in EQUIPOS), default=0) + 1

CLASES = [
    {"id": 1, "fecha": "2025-03-10"},
    {"id": 2, "fecha": "2025-03-17"},
]


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


@views_bp.route("/equipos")
def equipos():
    return render_template("equipos/listado.html", equipos=EQUIPOS)


@views_bp.route("/equipos/nuevo", methods=["GET", "POST"])
def equipo_nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        curso = request.form.get("curso", "").strip()
        estado = request.form.get("estado", "").strip() or "Activo"

        if not nombre or not descripcion or not curso:
            flash("Completa los campos obligatorios para crear el equipo.", "danger")
            return render_template("equipos/nuevo.html", equipo={"nombre": nombre, "descripcion": descripcion, "curso": curso, "estado": estado})

        EQUIPOS.append({
            "id": next_equipo_id(),
            "nombre": nombre,
            "descripcion": descripcion,
            "estado": estado,
            "miembros": 0,
            "curso": curso,
            "fecha_creacion": "Hoy",
        })
        flash("Equipo creado correctamente.", "success")
        return redirect(url_for("views.equipos"))

    return render_template("equipos/nuevo.html", equipo=None)


@views_bp.route("/equipos/<int:equipo_id>", methods=["GET", "POST"])
def equipo_detalle(equipo_id):
    equipo = get_equipo(equipo_id)
    if not equipo:
        return abort(404)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            EQUIPOS.remove(equipo)
            flash("Equipo eliminado correctamente.", "success")
            return redirect(url_for("views.equipos"))

        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        estado = request.form.get("estado", "").strip()

        if not nombre:
            flash("El nombre del equipo es obligatorio.", "danger")
        else:
            equipo["nombre"] = nombre
            equipo["descripcion"] = descripcion
            equipo["estado"] = estado or equipo["estado"]
            flash("Datos del equipo actualizados.", "success")
            return redirect(url_for("views.equipo_detalle", equipo_id=equipo_id))

    miembros = [
        {"padron": "12345", "nombre": "Luca", "apellido": "Perez"},
        {"padron": "12346", "nombre": "Ana", "apellido": "Gomez"},
        {"padron": "12347", "nombre": "Mica", "apellido": "Lopez"},
    ]

    return render_template("equipos/abm.html", equipo=equipo, miembros=miembros)



@views_bp.route("/equipos/<int:equipo_id>/delete", methods=["POST"])
def equipo_delete(equipo_id):
    equipo = get_equipo(equipo_id)
    if not equipo:
        return abort(404)
    EQUIPOS.remove(equipo)
    flash("Equipo eliminado correctamente.", "success")
    return redirect(url_for("views.equipos"))

@views_bp.route("/cursos/<int:id>/eliminar", methods=["POST"])
def curso_eliminar(id):
    global CURSOS
    CURSOS = [c for c in CURSOS if c["id"] != id]
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

