import requests
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from services.asistencia import obtener_clases_presenciales , calcular_clases_mes
from services.config import BACKEND_URL
from services.curso import obtener_cursos, obtener_curso
from services.equipo import (
    obtener_equipos,
    crear_equipo,
    obtener_equipo,
    editar_equipo,
    eliminar_equipo,
    obtener_miembros_equipo,
)
from services.login import usuario_logueado

views_bp = Blueprint("views", __name__)

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
    try:
        equipos = obtener_equipos()
    except RuntimeError as exc:
        flash(str(exc), "error")
        equipos = []

    cursos = obtener_cursos()
    cursos_map = {curso["id"]: curso["nombre"] for curso in cursos}

    for equipo in equipos:
        equipo["curso"] = cursos_map.get(equipo.get("curso_id"), f"Curso {equipo.get('curso_id')}")
        equipo["estado"] = equipo.get("estado", "Activo")
        equipo["miembros"] = equipo.get("miembros", 0)

    return render_template("equipos/listado.html", equipos=equipos)


@views_bp.route("/equipos/nuevo", methods=["GET", "POST"])
def equipo_nuevo():
    cursos = obtener_cursos()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        curso_id = request.form.get("curso_id", "").strip()

        if not nombre or not descripcion or not curso_id:
            flash("Completa los campos obligatorios para crear el equipo.", "danger")
            return render_template(
                "equipos/nuevo.html",
                equipo={"nombre": nombre, "descripcion": descripcion, "curso_id": int(curso_id) if curso_id.isdigit() else curso_id},
                cursos=cursos,
            )

        try:
            crear_equipo(nombre, descripcion, int(curso_id))
            flash("Equipo creado correctamente.", "success")
            return redirect(url_for("views.equipos"))
        except RuntimeError as exc:
            flash(str(exc), "error")
            return render_template(
                "equipos/nuevo.html",
                equipo={"nombre": nombre, "descripcion": descripcion, "curso_id": int(curso_id) if curso_id.isdigit() else curso_id},
                cursos=cursos,
            )

    return render_template("equipos/nuevo.html", equipo=None, cursos=cursos)


@views_bp.route("/equipos/<int:equipo_id>", methods=["GET", "POST"])
def equipo_detalle(equipo_id):
    try:
        equipo = obtener_equipo(equipo_id)
    except RuntimeError as exc:
        flash(str(exc), "error")
        return redirect(url_for("views.equipos"))

    if not equipo:
        flash("Equipo no encontrado.", "error")
        return redirect(url_for("views.equipos"))

    curso = obtener_curso(equipo.get("curso_id"))
    equipo["curso"] = curso["nombre"] if curso else f"Curso {equipo.get('curso_id')}"
    equipo["estado"] = equipo.get("estado", "Activo")
    equipo["miembros"] = equipo.get("miembros", 0)

    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            try:
                eliminar_equipo(equipo_id)
                flash("Equipo eliminado correctamente.", "success")
            except RuntimeError as exc:
                flash(str(exc), "error")
            return redirect(url_for("views.equipos"))

        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        estado = request.form.get("estado", "").strip()

        if not nombre:
            flash("El nombre del equipo es obligatorio.", "danger")
        else:
            try:
                editar_equipo(equipo_id, nombre, descripcion)
                flash("Datos del equipo actualizados.", "success")
                return redirect(url_for("views.equipo_detalle", equipo_id=equipo_id))
            except RuntimeError as exc:
                flash(str(exc), "error")

    try:
        miembros = obtener_miembros_equipo(equipo.get("curso_id"), equipo_id)
    except RuntimeError:
        miembros = []

    return render_template("equipos/abm.html", equipo=equipo, miembros=miembros)


@views_bp.route("/equipos/<int:equipo_id>/delete", methods=["POST"])
def equipo_delete(equipo_id):
    try:
        eliminar_equipo(equipo_id)
        flash("Equipo eliminado correctamente.", "success")
    except RuntimeError as exc:
        flash(str(exc), "error")
    return redirect(url_for("views.equipos"))


@views_bp.route("/cursos")
def cursos():
    page = int(request.args.get("page", 1))
    per_page = 10
    response = requests.get(
        f"{BACKEND_URL}/cursos",
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

'''
@views_bp.route("/alumnos")
def vista_alumnos():
    response = requests.get(f"{BACKEND_URL}/alumnos/")
    alumnos = response.json()

    return render_template("alumnos/listado.html", alumnos=alumnos)


@views_bp.route("/alumnos/<int:id>")
def detalle_alumno(id):
    response = requests.get(f"{BACKEND_URL}/alumnos/{id}")
    alumno = response.json()

    return render_template("alumnos/abm.html", alumno=alumno)
'''


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
        
        resultado = importar_alumnos_csv(file)

        if "error" in resultado:
               flash(resultado["error"], "error")
    
        elif len(resultado["errores"]) > 0:
              flash(resultado["errores"], "error")
     
        else:
             flash(f"Alumnos importados: {len(resultado['alumnos'])}", "success")

    return render_template("alumnos/csv.html")
