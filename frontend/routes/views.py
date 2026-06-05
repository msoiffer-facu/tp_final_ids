import requests
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from services.asistencia import obtener_clases_presenciales, obtener_clases_en_proceso
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
from services.login import usuario_logueado
from services.reporte import obtener_reporte_alumnos, obtener_reporte_equipos, obtener_estadisticas

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    if usuario_logueado():
        return redirect(url_for("views.dashboard"))
    return redirect(url_for("auth.login"))


@views_bp.route("/dashboard")
def dashboard():
    stats = {
        "total_alumnos": 0,
        "total_equipos": 0,
        "prom_asistencia": "0%",
        "notas_subidas": 0,
        "alumnos_promocionados": 0,
    }
    historial = [
        {"usuario": "Jose", "accion": "Subio las notas pendientes del pr...", "area": "Evaluaciones", "hora": "15/05/26 15:35"},
        {"usuario": "Marcos", "accion": "Doy de baja a un martin padron 123...", "area": "Alumnos", "hora": "14/05/26 21:35"},
        {"usuario": "Martin1", "accion": "Subio las notas pendientes del pr...", "area": "Evaluaciones", "hora": "14/05/26 13:02"},
    ]
    try:
        alumnos = requests.get(f"{BACKEND_URL}/alumnos/", timeout=5).json()
        equipos = requests.get(f"{BACKEND_URL}/equipos/", timeout=5).json()
        notas = requests.get(f"{BACKEND_URL}/notas", timeout=5).json()
        promedio = requests.get(f"{BACKEND_URL}/asistencia/promedio", timeout=5).json().get("promedio_asistencia", 0)
        alumnos_promocionados = sum(1 for n in notas if n.get("estado") == "PROMOCIONADO")
        stats = {
            "total_alumnos": len(alumnos),
            "total_equipos": len(equipos),
            "prom_asistencia": f"{round(promedio, 1)}%",
            "notas_subidas": len(notas),
            "alumnos_promocionados": alumnos_promocionados,
        }
    except Exception:
        pass

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
        resp_alumnos = requests.get(f"{BACKEND_URL}/alumnos/", timeout=5)
        todos_alumnos = resp_alumnos.json() if resp_alumnos.ok else []
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


@views_bp.route("/alumnos")
def vista_alumnos():
    try:
        resp = requests.get(f"{BACKEND_URL}/alumnos/", timeout=5)
        alumnos = resp.json() if resp.ok else []
    except Exception:
        alumnos = []
        flash("No se pudo conectar con el servidor.", "error")
    return render_template("alumnos/listado.html", alumnos=alumnos)


@views_bp.route("/alumnos/<int:id>")
def detalle_alumno(id):
    try:
        resp = requests.get(f"{BACKEND_URL}/alumnos/{id}", timeout=5)
        alumno = resp.json() if resp.ok else None
    except Exception:
        alumno = None
    if not alumno:
        flash("Alumno no encontrado.", "error")
        return redirect(url_for("views.vista_alumnos"))
    return render_template("alumnos/abm.html", alumno=alumno)


@views_bp.route("/alumnos/<int:id>/eliminar", methods=["POST"])
def eliminar_alumno(id):
    try:
        requests.delete(f"{BACKEND_URL}/alumnos/{id}", timeout=5)
        flash("Alumno eliminado correctamente.", "success")
    except Exception:
        flash("Error al eliminar el alumno.", "error")
    return redirect(url_for("views.vista_alumnos"))


@views_bp.route("/alumnos/importar", methods=["GET", "POST"])
def importar_csv():
    if request.method == "POST":
        file = request.files.get("file")
        if file is None:
            flash("Por favor, subí un archivo CSV", "error")
            return redirect(url_for("views.importar_csv"))

        resultado = requests.post(
            f"{BACKEND_URL}/alumnos/importar",
            files={"file": (file.filename, file.stream, file.content_type)},
            timeout=10,
        )
        if resultado.ok:
            data = resultado.json()
            flash(f"Alumnos importados: {data.get('insertados', 0)}", "success")
        else:
            flash("Error al importar el archivo.", "error")

    return render_template("alumnos/csv.html")
