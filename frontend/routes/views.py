from flask import Blueprint, render_template, redirect, url_for, request, session, flash
import requests
from services.asistencia import obtener_clases_presenciales , calcular_clases_mes
from services.curso import obtener_cursos
from services.login import usuario_logueado

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
    {"id": 1, "nombre": "Grupo 1", "descripcion": "TP Final", "fecha_creacion": "2025-03-01"},
]

CLASES = [
    {"id": 1, "fecha": "2025-03-10"},
    {"id": 2, "fecha": "2025-03-17"},
]


@views_bp.route("/")
def index():
    if usuario_logueado():
        return redirect(url_for("views.dashboard"))
    return redirect(url_for("auth.login"))


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
    return render_template("cursos/cursos.html", cursos=CURSOS)


@views_bp.route("/cursos/<int:id>")
def curso_detalle(id):
    curso = next((c for c in CURSOS if c["id"] == id), None)
    if not curso:
        return redirect(url_for("views.cursos"))
    return render_template("cursos/curso_detalle.html", curso=curso, alumnos=ALUMNOS, equipos=EQUIPOS, clases=CLASES)


@views_bp.route("/cursos/nuevo", methods=["GET", "POST"])
def curso_nuevo():
    if request.method == "POST":
        nuevo = {
            "id": len(CURSOS) + 1,
            "nombre": request.form.get("nombre"),
            "cuatrimestre": request.form.get("cuatrimestre"),
            "anio": int(request.form.get("anio")),
            "modificacion": request.form.get("modificacion"),
            "cantidad_alumnos": 0
        }
        CURSOS.append(nuevo)
        return redirect(url_for("views.cursos"))
    return render_template("cursos/curso_form.html", curso=None)


@views_bp.route("/cursos/<int:id>/editar", methods=["GET", "POST"])
def curso_editar(id):
    curso = next((c for c in CURSOS if c["id"] == id), None)
    if not curso:
        return redirect(url_for("views.cursos"))
    if request.method == "POST":
        curso["nombre"] = request.form.get("nombre")
        curso["cuatrimestre"] = request.form.get("cuatrimestre")
        curso["anio"] = int(request.form.get("anio"))
        curso["modificacion"] = request.form.get("modificacion")
        return redirect(url_for("views.curso_detalle", id=id))
    return render_template("cursos/curso_form.html", curso=curso)


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
