from flask import Blueprint, render_template, redirect, request, url_for, flash
from services.asistencia import obtener_clases_presenciales , calcular_clases_mes
from services.curso import obtener_cursos
import backend.routes.alumnos as importar_lista

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
    cursos = obtener_cursos()
    clases = obtener_clases_presenciales()
    clasesMes = calcular_clases_mes(clases)
    return render_template("alumnos/asistencia.html", clases=clases,cursos=cursos, clasesMes=clasesMes)

"""
@views_bp.route("/alumnos")
def vista_alumnos():
    response = requests.get("http://localhost:5000/alumnos/")
    alumnos = response.json()

    return render_template("alumnos/listado.html", alumnos=alumnos)


@views_bp.route("/alumnos/<int:id>")
def detalle_alumno(id):
    response = requests.get(f"http://localhost:5000/alumnos/{id}")
    alumno = response.json()

    return render_template("alumnos/abm.html", alumno=alumno)
"""


@views_bp.route("/alumnos")
def vista_alumnos():
    alumnos = [{"id": 1, "nombre": "Juan", "apellido": "Perez", "email": "juan@gmail.com", "padron": 12345, "abandono": False},
        {"id": 2, "nombre": "Ana", "apellido": "Gomez", "email": "ana@gmail.com", "padron": 54321, "abandono": True}]

    return render_template("alumnos/listado.html", alumnos=alumnos)

@views_bp.route("/alumnos/<int:id>")
def detalle_alumno(id):
    alumno = {"id": id, "nombre": "Juan", "apellido": "Perez", "email": "juan@gmail.com", "padron": 12345, "abandono": False}

    return render_template("alumnos/abm.html", alumno=alumno)



@views_bp.route("/alumnos/importar", methods=["GET", "POST"])
def importar_csv():
    if request.method == "POST":
        file = request.files.get("file")
        if file is None:
            flash("Por favor, subí un archivo CSV", "error")
            return redirect(url_for("views.importar_csv"))
        
        resultado = importar_lista(file)

        if "error" in resultado:
            flash(resultado["error"], "error")
        else:
            flash(f"Alumnos importados: {resultado['insertados']}", "success")
    return render_template("csv.html")