from flask import Blueprint, render_template, redirect, url_for, request, session, flash
import requests
from services.asistencia import *
from services.config import BACKEND_URL
from services.curso import obtener_cursos, obtener_curso
from services.equipo import (
    obtener_equipos,
    crear_equipo,
    obtener_equipo,
    editar_equipo,
    eliminar_equipo,
    obtener_miembros_equipo,
    agregar_alumno_equipo,
    quitar_alumno_equipo,
)
from services.login import usuario_logueado, limpiar_sesion, guardar_sesion
from services.reporte import obtener_reporte_alumnos, obtener_reporte_equipos, obtener_estadisticas
from services.alumnos_service import obtener_alumnos, obtener_alumno, actualizar_alumno, eliminar_alumno, importar_csv_service, crear_alumno

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    if usuario_logueado():
        return redirect(url_for("views.dashboard"))
    return redirect(url_for("auth.login"))


@views_bp.route("/dashboard")
def dashboard():
    stats = {}
    try:
        alumnos = requests.get(f"{BACKEND_URL}/alumnos").json()
        total_alumnos = len(alumnos)

        equipos = requests.get(f"{BACKEND_URL}/equipos").json()
        total_equipos = len(equipos)

        notas = requests.get(f"{BACKEND_URL}/notas").json()
        notas_subidas = len(notas)

        promedio_asistencia = requests.get(f"{BACKEND_URL}/asistencia/promedio").json().get("promedio_asistencia", 0)

        alumnos_promocionados = 0
        for nota in notas:
            if isinstance(nota, dict) and nota.get("estado") == "PROMOCIONADO":
                alumnos_promocionados += 1

        stats = {
            "total_alumnos": total_alumnos,
            "total_equipos": total_equipos,
            "prom_asistencia": round(promedio_asistencia, 2),
            "notas_subidas": notas_subidas,
            "alumnos_promocionados": alumnos_promocionados,
        }
    except Exception:
        stats = {
            "total_alumnos": 0,
            "total_equipos": 0,
            "prom_asistencia": 0,
            "notas_subidas": 0,
            "alumnos_promocionados": 0,
        }
    historial = [
        {"usuario": "Jose", "accion": "Subio las notas pendientes del pr...", "area": "Evaluaciones", "hora": "15/05/26 15:35"},
        {"usuario": "Marcos", "accion": "Doy de baja a un martin padron 123...", "area": "Alumnos", "hora": "14/05/26 21:35"},
        {"usuario": "Martin1", "accion": "Subio las notas pendientes del pr...", "area": "Evaluaciones", "hora": "14/05/26 13:02"},
    ]
    return render_template("dashboard.html", stats=stats, historial=historial, backend_url=BACKEND_URL)


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

    try:
        resp_alumnos = requests.get(f"{BACKEND_URL}/alumnos/todos", timeout=5)
        todos_alumnos = resp_alumnos.json() if resp_alumnos.ok else []
        if not isinstance(todos_alumnos, list):
            todos_alumnos = []
    except Exception:
        todos_alumnos = []

    ids_miembros = {str(m.get("id", m.get("alumno_id", ""))) for m in miembros}
    alumnos_disponibles = [a for a in todos_alumnos if str(a.get("id")) not in ids_miembros]

    return render_template("equipos/abm.html", equipo=equipo, miembros=miembros, alumnos_disponibles=alumnos_disponibles)


@views_bp.route("/equipos/<int:equipo_id>/alumnos/agregar", methods=["POST"])
def equipo_agregar_alumno(equipo_id):
    alumno_id = request.form.get("alumno_id")
    if not alumno_id:
        flash("Seleccioná un alumno.", "danger")
    else:
        try:
            agregar_alumno_equipo(equipo_id, int(alumno_id))
            flash("Alumno agregado al equipo.", "success")
        except RuntimeError as exc:
            flash(str(exc), "error")
    return redirect(url_for("views.equipo_detalle", equipo_id=equipo_id))


@views_bp.route("/equipos/<int:equipo_id>/alumnos/<int:alumno_id>/quitar", methods=["POST"])
def equipo_quitar_alumno(equipo_id, alumno_id):
    try:
        quitar_alumno_equipo(equipo_id, alumno_id)
        flash("Alumno quitado del equipo.", "success")
    except RuntimeError as exc:
        flash(str(exc), "error")
    return redirect(url_for("views.equipo_detalle", equipo_id=equipo_id))


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

        curso = requests.get(f"{BACKEND_URL}/cursos/{id}").json()
        alumnos_data = requests.get(f"{BACKEND_URL}/cursos/{id}/alumnos",
            params={"page": alumno_page, "per_page": alumno_per_page}).json()
        equipos_data = requests.get(f"{BACKEND_URL}/cursos/{id}/equipos",
            params={"page": equipo_page, "per_page": equipo_per_page}).json()
        clases = requests.get(f"{BACKEND_URL}/cursos/{id}/clases").json()
    except Exception:
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
        requests.post(f"{BACKEND_URL}/cursos", json=data)
        return redirect(url_for("views.cursos"))
    return render_template("cursos/curso_form.html", curso=None)


@views_bp.route("/cursos/<int:id>/editar", methods=["GET", "POST"])
def curso_editar(id):
    try:
        curso = requests.get(f"{BACKEND_URL}/cursos/{id}").json()
    except Exception:
        return redirect(url_for("views.cursos"))
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre"),
            "cuatrimestre": request.form.get("cuatrimestre"),
            "anio": int(request.form.get("anio")),
            "modificacion": request.form.get("modificacion")
        }
        requests.put(f"{BACKEND_URL}/cursos/{id}", json=data)
        return redirect(url_for("views.curso_detalle", id=id))
    return render_template("cursos/curso_form.html", curso=curso)


@views_bp.route("/cursos/<int:id>/eliminar", methods=["POST"])
def curso_eliminar(id):
    requests.delete(f"{BACKEND_URL}/cursos/{id}")
    return redirect(url_for("views.cursos"))

<<<<<<< HEAD

@views_bp.route("/reportes")
def reportes():
    tipo = request.args.get("tipo", "alumnos")
    filtros = {k: v for k, v in request.args.items() if k != "tipo" and v}

    datos = []
    columnas = []
    estadisticas = None
    error = None

    try:
        if tipo == "alumnos":
            resultado = obtener_reporte_alumnos(filtros)
            datos = resultado.get("data", [])
            if datos:
                columnas = list(datos[0].keys())
        elif tipo == "equipos":
            resultado = obtener_reporte_equipos(filtros)
            datos = resultado.get("data", [])
            if datos:
                columnas = list(datos[0].keys())
        elif tipo == "estadisticas":
            estadisticas = obtener_estadisticas()
    except RuntimeError as exc:
        error = str(exc)

    from urllib.parse import urlencode
    pdf_params = urlencode(filtros)
    pdf_url_alumnos = f"{BACKEND_URL}/api/reportes/alumnos/pdf?{pdf_params}"
    pdf_url_equipos = f"{BACKEND_URL}/api/reportes/equipos/pdf?{pdf_params}"
    pdf_url_estadisticas = f"{BACKEND_URL}/api/reportes/estadisticas/pdf"

    return render_template(
        "reportes/reportes.html",
        tipo=tipo,
        datos=datos,
        columnas=columnas,
        estadisticas=estadisticas,
        filtros=filtros,
        error=error,
        pdf_url_alumnos=pdf_url_alumnos,
        pdf_url_equipos=pdf_url_equipos,
        pdf_url_estadisticas=pdf_url_estadisticas,
    )


@views_bp.route("/asistencia", methods=["GET", "POST"])
def asistencia():
    page = int(request.args.get("page", 1))
    per_page = 10
    curso_id = request.args.get("curso", type=int)
    if request.method == "POST":
        curso_id_form = request.form.get("curso")
        data = {"curso_id": curso_id_form}
        try:
            response = requests.post(f"{BACKEND_URL}/asistencia", json=data)
            if response.ok:
                flash("Asistencia creada correctamente.", "success")
            else:
                flash(f"Error al crear la asistencia: {response.text}", "error")
        except Exception as e:
            flash(f"Error de conexión al crear la asistencia: {e}", "error")
        return redirect(url_for("views.asistencia"))

    cursos = obtener_cursos()
    clases_p = obtener_clases_presenciales(page, per_page, curso_id)
    clases_ep = obtener_clases_en_proceso()
    if not clases_p:
        clases_p = {"page": 0, "total_pages": 0}
        clases = []
    else:
        clases = clases_p['clases_presenciales']

    return render_template(
        "alumnos/asistencia.html",
        clases=clases,
        cursos=cursos,
        curso_id=curso_id,
        page=clases_p["page"],
        total_pages=clases_p["total_pages"],
        clases_en_proceso=clases_ep
    )


@views_bp.route("/asistencia/<int:id>")
def asistencia_detalle(id):
    clases = obtener_clases_presenciales()['clases_presenciales']
    clase = next((c for c in clases if c["id"] == id), None)
    if not clase:
        return redirect(url_for("views.asistencia"))

    alumnos = [
        {"id": 1, "padron": 12345, "nombre": "Juan", "apellido": "Perez", "email": "juan@mail.com", "abandono": True, "estado": False},
        {"id": 2, "padron": 67890, "nombre": "Maria", "apellido": "Garcia", "email": "maria@mail.com", "abandono": False, "estado": True},
    ]
    return render_template("alumnos/asistencia_detalle.html", alumnos=alumnos, registro=clase)


@views_bp.route("/asistencia/pedir-asistencia", methods=["POST"])
def asistencia_pedir():
    clase_id = request.form.get("asistencia")
    data = {"id_clase_p": clase_id}
    try:
        response = requests.post(f"{BACKEND_URL}/asistencia/pedir-asistencia", json=data)
        if response.ok:
            flash("QR de asistencia enviado correctamente.", "success")
        else:
            flash(f"Error al enviar el QR de asistencia: {response.text}", "error")
    except Exception as e:
        flash(f"Error de conexión al enviar el QR de asistencia: {e}", "error")
    return redirect(url_for("views.asistencia"))


@views_bp.route("/asistencia/verificar-asistencia", methods=["POST"])
def asistencia_verificar():
    token = request.form.get("token")
    clase_id = request.form.get("asistenciaEscanear")
    if not token:
        return "Token no enviado", 400
    if not clase_id:
        return "clase no seleccionada", 400
    try:
        response = requests.post(
            f"{BACKEND_URL}/asistencia/verificar-asistencia",
            json={"token": token, "clase_id": clase_id}
        )
    except Exception as e:
        return f"Error interno al conectar con backend: {e}", 500
    return response.text, response.status_code, {"Content-Type": "text/plain; charset=utf-8"}

=======

      
>>>>>>> 0406dfcc4617826b0153699730a0d4bd827c4ca1
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

# @views_bp.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")

#         if email == "a@test.com" and password == "1234":
#             session["user"] = {
#                 "email": email,
#                 "name": "Martin"
#             }
#             session["token"] = "prueba"

#             guardar_sesion(session["token"], session["user"])
#             flash(f"¡Bienvenido, {session["user"]["name"]}!", "success")
#             return redirect(url_for("views.dashboard"))

#     return render_template("login.html")

# @views_bp.route("/logout", methods=['POST'])
# def logout():
#     limpiar_sesion()
#     flash('Cerraste sesión.', 'success')
#     return redirect(url_for("views.login"))
