from flask import Blueprint, render_template, redirect, url_for

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
        {"usuario": "Jose", "accion": "Subio las notas pendientes del pr...", "area": "Evaluaciones", "hora": "15/05/26 15:35"},
        {"usuario": "Marcos", "accion": "Doy de baja a un martin padron 123...", "area": "Alumnos", "hora": "14/05/26 21:35"},
        {"usuario": "Martin1", "accion": "Subio las notas pendientes del pr...", "area": "Evaluaciones", "hora": "14/05/26 13:02"},
    ]
    return render_template("dashboard.html", stats=stats, historial=historial)
