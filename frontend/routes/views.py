from flask import Blueprint, Response, render_template, redirect, url_for, request, session, flash
from flask import Blueprint, render_template, redirect, url_for, request, session, flash
import requests
from services.asistencia import *
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
        "alumnos_promocionados": alumnos_promocionados
    }
        #historial = requests.get(f"{BACKEND_URL}/historial").json()

    except requests.RequestException:
        flash("Error al obtener datos del backend.", "danger")
        return render_template(("dashboard.html"),stats=stats)
   
    print("Promocionados:", alumnos_promocionados)
    return render_template("dashboard.html", stats=stats)



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
 
@views_bp.route("/alumnos/<int:id>")
def alumno_detalle(id):
    try:
     alumno = requests.get(f"{BACKEND_URL}/alumnos/{id}").json()
     equipos = requests.get(f"{BACKEND_URL}/equipos/{id}").json()
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

        return render_template(
            "alumnos/alumno_form.html",
            alumno=alumno
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

    data = {"nombre": nombre, "apellido": apellido, "email": email, "padron": padron, "abandono": abandono, "estado": estado}

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


@views_bp.route("/equipos")
def equipos():
    return render_template("equipos/listado.html", equipos=[])


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
        requests.post(f"{BACKEND_URL}/cursos", json=data)
        return redirect(url_for("views.cursos"))
    return render_template("cursos/curso_form.html", curso=None)


@views_bp.route("/cursos/<int:id>/editar", methods=["GET", "POST"])
def curso_editar(id):
    try:
        curso = requests.get(f"{BACKEND_URL}/cursos/{id}").json()
    except:
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
