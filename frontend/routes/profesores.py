from flask import Blueprint, render_template, redirect, url_for, request, flash

from services.profesores_service import (
    get_profesores,
    get_profesor,
    crear_profesor,
    actualizar_profesor,
    eliminar_profesor,
)

profesores_front_bp = Blueprint("profesores_front", __name__)


@profesores_front_bp.route("/profesores")
def profesores():
    ok, resultado = get_profesores()
    if not ok:
        flash(resultado, "error")
        resultado = []
    return render_template("profesores/listado.html", profesores=resultado)


@profesores_front_bp.route("/profesores/<int:profesor_id>")
def profesor_detalle(profesor_id):
    ok, resultado = get_profesor(profesor_id)
    if not ok:
        flash(resultado, "error")
        return redirect(url_for("profesores_front.profesores"))
    return render_template("profesores/detalle.html", profesor=resultado)


@profesores_front_bp.route("/profesores/nuevo", methods=["GET", "POST"])
def profesor_nuevo():
    if request.method == "POST":
        datos = {
            "nombre": request.form.get("nombre", "").strip(),
            "apellido": request.form.get("apellido", "").strip(),
            "email": request.form.get("email", "").strip(),
            "password": request.form.get("password", "").strip(),
        }
        ok, resultado = crear_profesor(datos)
        if not ok:
            flash(resultado, "error")
            return render_template("profesores/form.html", profesor=datos)

        flash("Profesor creado correctamente.", "success")
        return redirect(url_for("profesores_front.profesores"))

    return render_template("profesores/form.html", profesor=None)


@profesores_front_bp.route("/profesores/<int:profesor_id>/editar", methods=["GET", "POST"])
def profesor_editar(profesor_id):
    if request.method == "POST":
        datos = {
            "nombre": request.form.get("nombre", "").strip(),
            "apellido": request.form.get("apellido", "").strip(),
            "email": request.form.get("email", "").strip(),
        }
        password = request.form.get("password", "").strip()
        if password:
            datos["password"] = password

        ok, resultado = actualizar_profesor(profesor_id, datos)
        if not ok:
            flash(resultado, "error")
            profesor = {"id": profesor_id, **datos}
            return render_template("profesores/form.html", profesor=profesor)

        flash("Profesor actualizado correctamente.", "success")
        return redirect(url_for("profesores_front.profesores"))

    ok, resultado = get_profesor(profesor_id)
    if not ok:
        flash(resultado, "error")
        return redirect(url_for("profesores_front.profesores"))

    return render_template("profesores/form.html", profesor=resultado)


@profesores_front_bp.route("/profesores/<int:profesor_id>/eliminar", methods=["POST"])
def profesor_eliminar(profesor_id):
    ok, resultado = eliminar_profesor(profesor_id)
    if not ok:
        flash(resultado, "error")
    else:
        flash("Profesor eliminado correctamente.", "success")
    return redirect(url_for("profesores_front.profesores"))
