from flask import Blueprint, render_template, redirect, url_for, request, session, flash
import requests
from services.asistencia import obtener_clases_presenciales , calcular_clases_mes
from services.config import BACKEND_URL
from services.curso import obtener_cursos
from services.login import usuario_logueado, limpiar_sesion, guardar_sesion
from services.alumnos_service import obtener_alumnos, obtener_alumno, actualizar_alumno, eliminar_alumno, importar_csv_service, crear_alumno

views_bp = Blueprint("views", __name__)


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
        return "no encontrado", 404

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
        return "no encontrado", 404
    EQUIPOS.remove(equipo)
    flash("Equipo eliminado correctamente.", "success")
    return redirect(url_for("views.equipos"))


@views_bp.route("/cursos")
def cursos():
    page = int(request.args.get("page", 1))
    per_page = 10
    response = requests.get(
        f"http://localhost:5000/cursos",   
        params={"page": page, "per_page": per_page}
    )
    data = response.json()
    return render_template(
        "cursos/cursos.html",
        cursos=data["cursos"],
        page=data["page"],
        total_pages=data["total_pages"]
    )

@views_bp.route("/cursos/<int:id>")
def curso_detalle(id):
    try:
        alumno_page = int(request.args.get("alumno_page", 1))
        alumno_per_page = 10
        equipo_page = int(request.args.get("equipo_page", 1))
        equipo_per_page = 10

        curso = requests.get(f"http://localhost:5000/cursos/{id}").json()
        alumnos_data = requests.get(f"http://localhost:5000/cursos/{id}/alumnos",
            params={"page": alumno_page, "per_page": alumno_per_page}).json()
        equipos_data = requests.get(f"http://localhost:5000/cursos/{id}/equipos",
            params={"page": equipo_page, "per_page": equipo_per_page}).json()
        clases = requests.get(f"http://localhost:5000/cursos/{id}/clases").json()
    except:
        return redirect(url_for("views.cursos"))
    return render_template("cursos/curso_detalle.html",
        curso=curso,
        alumnos=alumnos_data["alumnos"],
        alumno_page=alumnos_data["page"],
        alumno_total_pages=alumnos_data["total_pages"],
        equipos=equipos_data["equipos"],
        equipo_page=equipos_data["page"],
        equipo_total_pages=equipos_data["total_pages"],
        clases=clases)

@views_bp.route("/cursos/nuevo", methods=["GET", "POST"])
def curso_nuevo():
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "cuatrimestre": request.form.get("cuatrimestre"),
            "anio": int(request.form.get("anio")),
            "modificacion": request.form.get("modificacion")
        }
        requests.post("http://localhost:5000/cursos", json=data)
        return redirect(url_for("views.cursos"))
    return render_template("cursos/curso_form.html", curso=None)


@views_bp.route("/cursos/<int:id>/editar", methods=["GET", "POST"])
def curso_editar(id):
    try:
        curso = requests.get(f"http://localhost:5000/cursos/{id}").json()
    except:
        return redirect(url_for("views.cursos"))
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "cuatrimestre": request.form.get("cuatrimestre"),
            "anio": int(request.form.get("anio")),
            "modificacion": request.form.get("modificacion")
        }
        requests.put(f"http://localhost:5000/cursos/{id}", json=data)
        return redirect(url_for("views.curso_detalle", id=id))
    return render_template("cursos/curso_form.html", curso=curso)


@views_bp.route("/cursos/<int:id>/eliminar", methods=["POST"])
def curso_eliminar(id):
    requests.delete(f"http://localhost:5000/cursos/{id}")
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

@views_bp.route("/alumnos")
def vista_alumnos():
    pagina = request.args.get("pagina", default=1, type=int)
    busqueda = request.args.get("busqueda", default="", type=str)
    abandono = request.args.get("abandono", default="", type=str)
    resultado = obtener_alumnos(pagina, busqueda, abandono)

    if resultado["status_code"] != 200:
        flash(resultado["data"].get("error", "Error al cargar alumnos"), "error")
        return render_template("alumnos/listado.html", alumnos=[], pagina=pagina, total=0, limit=10, total_pages=0)

    inicio = max(1, pagina - 1)
    fin = min(resultado["data"]["total_pages"], pagina + 1)

    return render_template(
        "alumnos/listado.html",
        fin=fin,
        inicio=inicio,
        alumnos=resultado["data"]["alumnos"],
        limit=resultado["data"]["limit"],
        total=resultado["data"]["total"],
        pagina=pagina,
        total_pages=resultado["data"]["total_pages"]
    )

@views_bp.route("/alumnos/<int:id>")
def detalle_alumno(id):
    resultado = obtener_alumno(id)

    if resultado["status_code"] != 200:
        flash(resultado["data"].get("error", "Error al cargar el alumno"), "error")
        return redirect(url_for("views.vista_alumnos"))
    return render_template("alumnos/abm.html", alumno=resultado["data"])


@views_bp.route("/alumnos/<int:id>/editar", methods=["GET", "POST"])
def editar_alumno(id):
    if request.method == "POST":
        actualizado = {
            "padron": request.form.get("padron"),
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "email": request.form.get("email"),
            "abandono": request.form.get("abandono")
        }

        resultado = actualizar_alumno(id, actualizado)
        
        if resultado["status_code"] == 200:
            flash("Alumno actualizado correctamente.", "success")
        else: 
            flash(resultado["data"].get("error", "Error al actualizar el alumno"), "error")
        return redirect(url_for("views.vista_alumnos"))

    return redirect(url_for("views.detalle_alumno", id=id))

@views_bp.route("/alumnos/<int:id>/eliminar", methods=["POST"])
def eliminar_alumnos(id):
    resultado = eliminar_alumno(id)
    if resultado["status_code"] == 200:
        flash("Alumno eliminado correctamente.", "success")
    else:
        flash(resultado["data"].get("error", "Error al eliminar el alumno"), "error")
    return redirect(url_for("views.vista_alumnos"))

@views_bp.route("/alumnos/importar", methods=["GET", "POST"])
def importar_csv():
    if request.method == "POST":
        file = request.files.get("file")
        if file is None:
            flash("Por favor, subí un archivo CSV", "error")
            return redirect(url_for("views.importar_csv"))
        
        resultado = importar_csv_service(file)

        if resultado["status_code"] != 200:
            flash(resultado["data"].get("error", "Error al importar el archivo"), "error")
            return redirect(url_for("views.importar_csv"))

        insertados = resultado["data"].get("insertados", 0)
        existentes = resultado["data"].get("existentes", 0)
        flash(f"Importación completada: {insertados} insertados, {existentes} existentes.", "success")

        if resultado["data"].get("errores"):
             flash("Errores en el CSV: " + ", ".join(resultado["data"]["errores"]), "error")
        return redirect(url_for("views.vista_alumnos"))

    return render_template("alumnos/csv.html")

@views_bp.route("/alumnos/nuevo", methods=["GET", "POST"])
def nuevo_alumno():
    if request.method == "POST":
        nuevo = {
            "padron": request.form.get("padron"),
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "email": request.form.get("email"),
            "abandono": request.form.get("abandono")
        }
        resultado = crear_alumno(nuevo)
        if resultado["status_code"] == 201:
            flash("Alumno creado correctamente.", "success")
        else:
            flash(resultado["data"].get("error", "Error al crear el alumno"), "error")
        return redirect(url_for("views.vista_alumnos"))
    return render_template("alumnos/abm.html", alumno=None)