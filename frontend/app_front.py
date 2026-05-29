from flask import Flask, redirect, request, url_for
from routes.views import views_bp
from routes.authenticacion_views import auth_bp
from services.login import usuario_logueado

app = Flask(__name__)

app.register_blueprint(views_bp)
app.register_blueprint(auth_bp)
app.config["SECRET_KEY"] = "clave-secreta"


@app.before_request
def control_acceso():
    if request.endpoint == "static":
        return None

    logueado = usuario_logueado()

    if request.endpoint == "auth.login":
        if logueado:
            return redirect(url_for("views.dashboard"))
        return None

    if not logueado:
        return redirect(url_for("auth.login"))

    return None


if __name__ == "__main__":
    app.run(debug=True, port=5001)
