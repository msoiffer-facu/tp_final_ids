from datetime import date, datetime

from flask import Blueprint, render_template, redirect, url_for, request, flash
from services.evaluaciones_service import (
    get_evaluaciones,
    get_evaluacion,
    crear_evaluacion,
    actualizar_evaluacion,
    eliminar_evaluacion,
    get_tipos,
    get_tipo,
    crear_tipo,
    actualizar_tipo,
    eliminar_tipo,
    get_notas_evaluacion,
    guardar_notas_evaluacion,
)
from services.curso import obtener_cursos

evaluaciones_front_bp = Blueprint("evaluaciones_front", __name__)


def _parse_fecha(fecha):
    if isinstance(fecha, datetime):
        return fecha
    if isinstance(fecha, date):
        return datetime.combine(fecha, datetime.min.time())
    if not fecha:
        return None

    fecha = str(fecha)
    try:
        return datetime.fromisoformat(fecha.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        pass

    for formato in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%a, %d %b %Y %H:%M:%S %Z"):
        try:
            return datetime.strptime(fecha, formato)
        except ValueError:
            pass
    return None


def _formatear_fecha(fecha):
    fecha_parseada = _parse_fecha(fecha)
    if fecha_parseada:
        return fecha_parseada.strftime("%d/%m/%Y %H:%M")
    return fecha or "-"


def _preparar_evaluacion_form(evaluacion):
    if not evaluacion:
        return evaluacion

    fecha_parseada = _parse_fecha(evaluacion.get("fecha"))
    if fecha_parseada:
        evaluacion["fecha"] = fecha_parseada.strftime("%Y-%m-%d")
        evaluacion["hora"] = fecha_parseada.strftime("%H:%M")
    else:
        evaluacion["hora"] = evaluacion.get("hora", "")
    return evaluacion


def _fecha_con_hora():
    fecha = request.form.get("fecha")
    hora = request.form.get("hora") or "00:00"
    if fecha:
        return f"{fecha} {hora}:00"
    return fecha


# ─── TIPOS DE EVALUACIÓN ───

@evaluaciones_front_bp.route("/evaluaciones/tipos")
def tipos_listado():
    ok, resultado = get_tipos()
    if not ok:
        flash(resultado, "error")
        resultado = []
    return render_template("evaluaciones/tipos.html", tipos=resultado)


@evaluaciones_front_bp.route("/evaluaciones/tipos/nuevo", methods=["GET", "POST"])
def tipo_nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            flash("El nombre es obligatorio.", "error")
            return render_template("evaluaciones/tipo_form.html", tipo=None)
        ok, resultado = crear_tipo({"nombre": nombre})
        if not ok:
            flash(resultado, "error")
            return render_template("evaluaciones/tipo_form.html", tipo={"nombre": nombre})
        flash("Tipo de evaluación creado correctamente.", "success")
        return redirect(url_for("evaluaciones_front.tipos_listado"))
    return render_template("evaluaciones/tipo_form.html", tipo=None)


@evaluaciones_front_bp.route("/evaluaciones/tipos/<int:tipo_id>/editar", methods=["GET", "POST"])
def tipo_editar(tipo_id):
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            flash("El nombre es obligatorio.", "error")
            return render_template("evaluaciones/tipo_form.html", tipo={"id": tipo_id, "nombre": nombre})
        ok, resultado = actualizar_tipo(tipo_id, {"nombre": nombre})
        if not ok:
            flash(resultado, "error")
            return render_template("evaluaciones/tipo_form.html", tipo={"id": tipo_id, "nombre": nombre})
        flash("Tipo de evaluación actualizado correctamente.", "success")
        return redirect(url_for("evaluaciones_front.tipos_listado"))

    ok, tipo = get_tipo(tipo_id)
    if not ok:
        flash(tipo, "error")
        return redirect(url_for("evaluaciones_front.tipos_listado"))
    return render_template("evaluaciones/tipo_form.html", tipo=tipo)


@evaluaciones_front_bp.route("/evaluaciones/tipos/<int:tipo_id>/eliminar", methods=["POST"])
def tipo_eliminar(tipo_id):
    ok, resultado = eliminar_tipo(tipo_id)
    if not ok:
        flash(resultado, "error")
    else:
        flash("Tipo de evaluación eliminado correctamente.", "success")
    return redirect(url_for("evaluaciones_front.tipos_listado"))


# ─── EVALUACIONES ───

@evaluaciones_front_bp.route("/evaluaciones")
def evaluaciones_listado():
    page = request.args.get("page", 1, type=int)
    per_page = 10
    tipo_id = request.args.get("tipo_id", None, type=int)
    curso_id = request.args.get("curso_id", None, type=int)

    ok, resultado = get_evaluaciones(page, per_page, tipo_id, curso_id)
    if not ok:
        flash(resultado, "error")
        resultado = {"evaluaciones": [], "page": 1, "total_pages": 1, "total": 0}

    ok_tipos, tipos = get_tipos()
    if not ok_tipos:
        tipos = []

    cursos = obtener_cursos() or []
    evaluaciones = resultado.get("evaluaciones", [])
    for evaluacion in evaluaciones:
        evaluacion["fecha_formateada"] = _formatear_fecha(evaluacion.get("fecha"))

    return render_template(
        "evaluaciones/listado.html",
        evaluaciones=evaluaciones,
        page=resultado.get("page", 1),
        total_pages=resultado.get("total_pages", 1),
        total=resultado.get("total", 0),
        tipos=tipos,
        cursos=cursos,
        tipo_id_filtro=tipo_id,
        curso_id_filtro=curso_id,
    )


@evaluaciones_front_bp.route("/evaluaciones/nuevo", methods=["GET", "POST"])
def evaluacion_nueva():
    if request.method == "POST":
        datos = {
            "titulo": request.form.get("titulo", "").strip(),
            "fecha": _fecha_con_hora(),
            "hora": request.form.get("hora"),
            "tipo_id": request.form.get("tipo_id", type=int),
            "curso_id": request.form.get("curso_id", type=int),
        }
        ok, resultado = crear_evaluacion(datos)
        if not ok:
            flash(resultado, "error")
            ok_tipos, tipos = get_tipos()
            cursos = obtener_cursos() or []
            datos = _preparar_evaluacion_form(datos)
            return render_template("evaluaciones/form.html", evaluacion=datos, tipos=tipos if ok_tipos else [], cursos=cursos)
        flash("Evaluación creada correctamente.", "success")
        return redirect(url_for("evaluaciones_front.evaluaciones_listado"))

    ok_tipos, tipos = get_tipos()
    cursos = obtener_cursos() or []
    return render_template("evaluaciones/form.html", evaluacion=None, tipos=tipos if ok_tipos else [], cursos=cursos)


@evaluaciones_front_bp.route("/evaluaciones/<int:evaluacion_id>/editar", methods=["GET", "POST"])
def evaluacion_editar(evaluacion_id):
    if request.method == "POST":
        datos = {
            "titulo": request.form.get("titulo", "").strip(),
            "fecha": _fecha_con_hora(),
            "hora": request.form.get("hora"),
            "tipo_id": request.form.get("tipo_id", type=int),
            "curso_id": request.form.get("curso_id", type=int),
        }
        ok, resultado = actualizar_evaluacion(evaluacion_id, datos)
        if not ok:
            flash(resultado, "error")
            ok_tipos, tipos = get_tipos()
            cursos = obtener_cursos() or []
            datos["id"] = evaluacion_id
            datos = _preparar_evaluacion_form(datos)
            return render_template("evaluaciones/form.html", evaluacion=datos, tipos=tipos if ok_tipos else [], cursos=cursos)
        flash("Evaluación actualizada correctamente.", "success")
        return redirect(url_for("evaluaciones_front.evaluaciones_listado"))

    ok, evaluacion = get_evaluacion(evaluacion_id)
    if not ok:
        flash(evaluacion, "error")
        return redirect(url_for("evaluaciones_front.evaluaciones_listado"))
    ok_tipos, tipos = get_tipos()
    cursos = obtener_cursos() or []
    evaluacion = _preparar_evaluacion_form(evaluacion)
    return render_template("evaluaciones/form.html", evaluacion=evaluacion, tipos=tipos if ok_tipos else [], cursos=cursos)


@evaluaciones_front_bp.route("/evaluaciones/<int:evaluacion_id>/eliminar", methods=["POST"])
def evaluacion_eliminar(evaluacion_id):
    ok, resultado = eliminar_evaluacion(evaluacion_id)
    if not ok:
        flash(resultado, "error")
    else:
        flash("Evaluación eliminada correctamente.", "success")
    return redirect(url_for("evaluaciones_front.evaluaciones_listado"))


# ─── NOTAS ───

@evaluaciones_front_bp.route("/evaluaciones/<int:evaluacion_id>/notas", methods=["GET", "POST"])
def evaluacion_notas(evaluacion_id):
    ok_ev, evaluacion = get_evaluacion(evaluacion_id)
    if not ok_ev:
        flash(evaluacion, "error")
        return redirect(url_for("evaluaciones_front.evaluaciones_listado"))
    evaluacion["fecha_formateada"] = _formatear_fecha(evaluacion.get("fecha"))

    if request.method == "POST":
        alumno_ids = request.form.getlist("alumno_id")
        notas_raw = request.form.getlist("nota_alumno")
        notas = []
        for aid, nota in zip(alumno_ids, notas_raw):
            nota = nota.strip()
            if nota:
                notas.append({"alumno_id": int(aid), "nota_alumno": float(nota)})

        if not notas:
            flash("No se ingresó ninguna nota.", "error")
        else:
            ok, resultado = guardar_notas_evaluacion(evaluacion_id, notas)
            if not ok:
                flash(resultado, "error")
            else:
                flash("Notas guardadas correctamente.", "success")
        return redirect(url_for("evaluaciones_front.evaluacion_notas", evaluacion_id=evaluacion_id))

    ok_notas, notas = get_notas_evaluacion(evaluacion_id)
    if not ok_notas:
        flash(notas, "error")
        notas = []

    return render_template("evaluaciones/notas.html", evaluacion=evaluacion, notas=notas)
