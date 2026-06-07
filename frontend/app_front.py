import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from flask import Flask, redirect, request, url_for
from routes.authenticacion_views import auth_bp
from routes.views import views_bp
from routes.profesores import profesores_front_bp
from routes.evaluaciones import evaluaciones_front_bp
from routes.asistencia import asistencia_front_bp
from services.login import usuario_logueado


app = Flask(__name__)

app.register_blueprint(views_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(profesores_front_bp)
app.register_blueprint(evaluaciones_front_bp)
app.register_blueprint(asistencia_front_bp)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave-secreta")



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
    app.run(debug=True, port=os.environ.get("PORT", 5001))
