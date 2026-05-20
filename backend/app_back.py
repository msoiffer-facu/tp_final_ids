import os

from flask import Flask
from routes.login import *
from routes.asistencia import asistencia_bp
from routes.profesores import profesores_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

app.register_blueprint(profesores_bp, url_prefix="/profesores")

app.register_blueprint(asistencia_bp, url_prefix="/asistencia")


@app.route("/")
def home():
    return "Hola Flask"

if __name__ == "__main__":
    app.run(debug=True)
