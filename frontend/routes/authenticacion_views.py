from flask import Blueprint, render_template, redirect, url_for, request, flash
from services.login import autenticar, guardar_sesion, limpiar_sesion, cerrar_sesion_backend

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        ok, resultado = autenticar(email, password)
        if ok:
            usuario, cookies = resultado
            guardar_sesion(usuario, cookies)
            flash(f"¡Bienvenido, {usuario['name']}!", "success")
            return redirect(url_for("views.dashboard"))

        flash(resultado, "error")

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    cerrar_sesion_backend()
    limpiar_sesion()
    flash("Cerraste sesión.", "success")
    return redirect(url_for("auth.login"))
