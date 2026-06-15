from flask import Blueprint, Response, render_template, redirect, url_for, request, session, flash
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
    asociar_equipo_evaluacion,
    obtener_evaluaciones_equipo,
    desasociar_equipo_evaluacion,
)
from services.evaluaciones_service import get_evaluaciones
from services.login import usuario_logueado, limpiar_sesion, guardar_sesion
from services.alumnos_service import obtener_alumnos, obtener_alumno, actualizar_alumno, eliminar_alumno, importar_csv_service, crear_alumno

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    if usuario_logueado():
        return redirect(url_for("views.dashboard"))
    return redirect(url_for("auth.login"))


@views_bp.route("/inicio")
def inicio():
    info_cursada = [
        {"label": "Cuatrimestre", "valor": "2do - 2026"},
        {"label": "Carga horaria", "valor": "6 hs semanales"},
        {"label": "Modalidad", "valor": "Presencial/virtual"},
    ]
    contenidos = [
        {"titulo": "Bases de datos MySQL", "descripcion": "Diseño de tablas, consultas SQL, INSERT, UPDATE y JOINs."},
        {"titulo": "Linux y Bash", "descripcion": "Terminal, comandos, scripting y manejo del sistema de archivos."},
        {"titulo": "Backend con Python y Flask", "descripcion": "APIs RESTful, endpoints, manejo de requests y responses."},
        {"titulo": "Git y GitHub", "descripcion": "Control de versiones, ramas, commits y trabajo colaborativo."},
        {"titulo": "Docker y despliegue", "descripcion": "Contenedores, imágenes, Docker Compose y entornos reproducibles."},
        {"titulo": "Frontend: HTML, CSS y JS", "descripcion": "Interfaces web conectadas al backend usando Flask como servidor."},
    ]
    return render_template(
        "inicio.html",
        info_cursada=info_cursada,
        contenidos=contenidos,
    )


@views_bp.route("/dashboard")
def dashboard():
    stats = {}
    chart_data = {"labels": [], "c1": [], "c2": [], "cursos": {}}
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
        "alumnos_promocionados": alumnos_promocionados
    }

        promocionados_response = requests.get(
            f"{BACKEND_URL}/api/reportes/promocionados/cuatrimestre"
        )
        promocionados_response.raise_for_status()
        promocionados = promocionados_response.json().get("data", [])
        chart_periodos = {}
        for item in promocionados:
            anio, cuatrimestre = item["periodo"].split("-C", 1)
            chart_periodos.setdefault(anio, {})
            chart_periodos[anio][cuatrimestre] = item

        labels = sorted(chart_periodos.keys())
        chart_data = {
            "labels": labels,
            "c1": [
                chart_periodos[anio].get("1", {}).get("promedio", 0)
                for anio in labels
            ],
            "c2": [
                chart_periodos[anio].get("2", {}).get("promedio", 0)
                for anio in labels
            ],
            "cursos": {
                anio: {
                    "1": chart_periodos[anio].get("1", {}).get("cursos", []),
                    "2": chart_periodos[anio].get("2", {}).get("cursos", []),
                }
                for anio in labels
            },
        }

    except requests.RequestException:
        flash("Error al obtener datos del backend.", "danger")
        return render_template(("dashboard.html"),stats=stats, chart_data=chart_data)
   
    print("Promocionados:", alumnos_promocionados)
    return render_template("dashboard.html", stats=stats, chart_data=chart_data)



@views_bp.route("/alumnos/pdf")
def alumnos_pdf():
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/reportes/alumnos/pdf"
        )

        return Response(
            response.content,
            content_type="application/pdf",
            headers={
                "Content-Disposition":
                "attachment; filename=reporte_alumnos.pdf"
            }
        )

    except requests.RequestException:
        flash("Error al generar PDF.", "danger")
        return render_template("dashboard.html")


@views_bp.route("/equipos/pdf")
def equipos_pdf():
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/reportes/equipos/pdf"
        )

        return Response(
            response.content,
            content_type="application/pdf",
            headers={
                "Content-Disposition":
                "attachment; filename=reporte_equipos.pdf"
            }
        )

    except requests.RequestException:
        flash("Error al generar PDF.", "danger")
        return render_template("dashboard.html")



@views_bp.route("/estadisticas/pdf")
def estadisticas_pdf():
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/reportes/estadisticas/pdf"
        )

        return Response(
            response.content,
            content_type="application/pdf",
            headers={
                "Content-Disposition":
                "attachment; filename=reporte_estadisticas.pdf"
            }
        )

    except requests.RequestException:
        flash("Error al generar PDF.", "danger")
        return render_template("dashboard.html")


@views_bp.route("/alumnos/csv")
def alumnos_csv():
    try:
        response = requests.get(f"{BACKEND_URL}/api/reportes/alumnos/csv")
        response.raise_for_status()

        return Response(
            response.content,
            content_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                "attachment; filename=reporte_alumnos.csv"
            }
        )

    except requests.RequestException:
        flash("Error al generar CSV.", "danger")
        return redirect(url_for("views.dashboard"))


@views_bp.route("/equipos/csv")
def equipos_csv():
    try:
        response = requests.get(f"{BACKEND_URL}/api/reportes/equipos/csv")
        response.raise_for_status()

        return Response(
            response.content,
            content_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                "attachment; filename=reporte_equipos.csv"
            }
        )

    except requests.RequestException:
        flash("Error al generar CSV.", "danger")
        return redirect(url_for("views.dashboard"))


@views_bp.route("/estadisticas/csv")
def estadisticas_csv():
    try:
        response = requests.get(f"{BACKEND_URL}/api/reportes/estadisticas/csv")
        response.raise_for_status()

        return Response(
            response.content,
            content_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                "attachment; filename=reporte_estadisticas.csv"
            }
        )

    except requests.RequestException:
        flash("Error al generar CSV.", "danger")
        return redirect(url_for("views.dashboard"))
 
@views_bp.route("/alumnos/<int:id>")
def alumno_detalle(id):
    try:
     alumno = requests.get(f"{BACKEND_URL}/alumnos/{id}").json()
     equipos = requests.get(f"{BACKEND_URL}/equipos/alumno/{id}").json()
     if isinstance(equipos, dict):
          equipos = [equipos]  
     notas = requests.get(f"{BACKEND_URL}/notas/alumno/{id}").json()
     asistencias = requests.get(f"{BACKEND_URL}/asistencia/alumno/{id}").json()

     print("ALUMNO")
     print(alumno)
     print("EQUIPOS")
     print(equipos)
     print("NOTAS")
     print(notas)
     print("ASISTENCIAS")
     print(asistencias)


     return render_template("alumnos/alumno_detalle.html", alumno=alumno, equipos=equipos, notas=notas, asistencias=asistencias)

    except Exception as e:
        flash(f"Error al obtener datos del alumno: {e}", "danger")
        return redirect(url_for("views.dashboard"))

@views_bp.route("/alumnos/<int:id>/editar", methods=["GET"])
def alumno_form(id):
    try:
        response = requests.get(f"{BACKEND_URL}/alumnos/{id}")
        if not response:
            flash("Error al obtener el alumno", "danger")
            return redirect(url_for("views.vista_alumnos"))
       
        alumno = response.json()
        cursos = obtener_cursos()

        return render_template(
            "alumnos/alumno_form.html",
            alumno=alumno,
            cursos=cursos
        )

    except requests.RequestException:
    
        flash("Error al obtener el alumno.", "danger")
        return redirect(url_for("views.vista_alumnos"))

@views_bp.route("/alumnos/<int:id>/editar", methods=["POST"])
def alumno_editar(id):
    print("entro a editar")
    nombre = request.form.get("nombre")
    apellido = request.form.get("apellido")
    email = request.form.get("email")
    padron = request.form.get("padron")
    abandono = request.form.get("abandono") == "true"
    estado = request.form.get("estado") == "true"
    curso_id = request.form.get("curso")

    data = {"nombre": nombre, "apellido": apellido, "email": email, "padron": padron, "abandono": abandono, "estado": estado, "curso_id": curso_id}

    try:
        response = requests.put(f"{BACKEND_URL}/alumnos/{id}", json=data)
        if response.ok:
            flash("Alumno actualizado correctamente.", "success")
        else:
            flash(f"Error al actualizar el alumno: {response.text}", "danger")
    except Exception as e:
        flash(f"Error de conexión al actualizar el alumno: {e}", "danger")

    return redirect(url_for("views.alumno_detalle", id=id))


@views_bp.route("/alumnos/<int:id>/eliminar", methods=["POST"])
def eliminar_alumno(id):
    try:
        response = requests.delete(f"{BACKEND_URL}/alumnos/{id}")
        response.raise_for_status()

        flash("Alumno eliminado correctamente.", "success")

    except requests.RequestException as e:
        error_msg = ""

        if response is not None:
            try:
                error_msg = response.json().get("error", response.text)
            except Exception:
                error_msg = response.text
        else:
            error_msg = str(e)

        print("ERROR:", e)
        flash(f"Error al eliminar alumno: {error_msg}", "danger")

    return redirect(url_for("views.vista_alumnos"))

@views_bp.route("/alumnos/exportar", methods=["GET"])
def exportar_alumnos():
    return redirect(f"{BACKEND_URL}/alumnos/exportar")


# ── Equipos ──────────────────────────────────────────────────────────────────

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
        equipo["estado"] = equipo.get("estado") or "Activo"
        equipo["miembros"] = equipo.get("miembros", 0)

    return render_template("equipos/listado.html", equipos=equipos)


@views_bp.route("/equipos/nuevo", methods=["GET", "POST"])
def equipo_nuevo():
    cursos = obtener_cursos()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        curso_id = request.form.get("curso_id", "").strip()

        if not nombre or not curso_id:
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
    equipo["estado"] = equipo.get("estado") or "Activo"
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
        estado = request.form.get("estado", "Activo").strip()

        if not nombre:
            flash("El nombre del equipo es obligatorio.", "danger")
        else:
            try:
                editar_equipo(equipo_id, nombre, descripcion, estado)
                flash("Datos del equipo actualizados.", "success")
                return redirect(url_for("views.equipo_detalle", equipo_id=equipo_id))
            except RuntimeError as exc:
                flash(str(exc), "error")

    try:
        miembros = obtener_miembros_equipo(equipo.get("curso_id"), equipo_id)
    except RuntimeError:
        miembros = []

    equipo["miembros"] = len(miembros)

    try:
        evaluaciones_asociadas = obtener_evaluaciones_equipo(equipo_id)
        if not isinstance(evaluaciones_asociadas, list):
            evaluaciones_asociadas = []
    except RuntimeError:
        evaluaciones_asociadas = []

    curso_id = equipo.get("curso_id")
    try:
        resp_alumnos = requests.get(f"{BACKEND_URL}/cursos/{curso_id}/alumnos", params={"per_page": 1000}, timeout=5)
        data_alumnos = resp_alumnos.json() if resp_alumnos.ok else {}
        todos_alumnos = data_alumnos.get("alumnos", []) if isinstance(data_alumnos, dict) else []
    except Exception:
        todos_alumnos = []

    ids_miembros = {str(m.get("id", m.get("alumno_id", ""))) for m in miembros}
    alumnos_disponibles = [a for a in todos_alumnos if str(a.get("id")) not in ids_miembros]

    evaluaciones = []
    try:
        ok, data_ev = get_evaluaciones(per_page=1000, curso_id=curso_id)
        if ok and isinstance(data_ev, dict):
            evaluaciones = data_ev.get("evaluaciones", [])
    except Exception:
        evaluaciones = []

    return render_template("equipos/abm.html", equipo=equipo, miembros=miembros, alumnos_disponibles=alumnos_disponibles, evaluaciones=evaluaciones, evaluaciones_asociadas=evaluaciones_asociadas)


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


@views_bp.route("/equipos/<int:equipo_id>/evaluacion/<int:evaluacion_id>/quitar", methods=["POST"])
def equipo_desasociar_evaluacion(equipo_id, evaluacion_id):
    try:
        desasociar_equipo_evaluacion(equipo_id, evaluacion_id)
        flash("Evaluación desasociada correctamente.", "success")
    except RuntimeError as exc:
        flash(str(exc), "error")
    return redirect(url_for("views.equipo_detalle", equipo_id=equipo_id))


@views_bp.route("/equipos/<int:equipo_id>/evaluacion", methods=["POST"])
def equipo_asociar_evaluacion(equipo_id):
    evaluacion_id = request.form.get("evaluacion_id")
    if not evaluacion_id:
        flash("Seleccioná una evaluación.", "danger")
    else:
        try:
            asociar_equipo_evaluacion(equipo_id, int(evaluacion_id))
            flash("Equipo asociado a la evaluación correctamente.", "success")
        except RuntimeError as exc:
            flash(str(exc), "error")
    return redirect(url_for("views.equipo_detalle", equipo_id=equipo_id))


# ── Cursos ────────────────────────────────────────────────────────────────────

@views_bp.route("/cursos")
def cursos():
    page = int(request.args.get("page", 1))
    cuatrimestre = request.args.get("cuatrimestre", "")
    per_page = 10
    params = {"page": page, "per_page": per_page}
    if cuatrimestre:
        params["cuatrimestre"] = cuatrimestre
    response = requests.get(f"{BACKEND_URL}/cursos", params=params)
    data = response.json()
    return render_template(
        "cursos/cursos.html",
        cursos=data["cursos"],
        page=data["page"],
        total_pages=data["total_pages"],
        cuatrimestre=cuatrimestre
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


# ── Alumnos (del compañero, sin modificar) ────────────────────────────────────

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
        abanono = False
        nuevo = {
            "padron": request.form.get("padron"),
            "nombre": request.form.get("nombre"),
            "apellido": request.form.get("apellido"),
            "email": request.form.get("email"),
            "abandono": abanono,
            "curso_id":request.form.get("curso")
        }
        resultado = crear_alumno(nuevo)
        if resultado["status_code"] == 201:
            flash("Alumno creado correctamente.", "success")
        else:
            flash(resultado["data"].get("error", "Error al crear el alumno"), "error")
        return redirect(url_for("views.vista_alumnos"))
    cursos = obtener_cursos()
    return render_template("alumnos/abm.html", alumno=None, cursos=cursos)
