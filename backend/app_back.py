import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

from flask import Flask
from routes.asistencia import asistencia_bp
from routes.profesores import profesores_bp
from routes.evaluaciones import evaluaciones_bp
from routes.notas import notas_bp
from routes.reportes import reportes_bp
from routes.alumnos import alumnos_bp
from routes.cursos import cursos_bp
from routes.equipos import equipos_bp
import sys

import socket


_orig_getaddrinfo = socket.getaddrinfo

def _ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = _ipv4_only


BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

app.register_blueprint(profesores_bp, url_prefix="/profesores")
app.register_blueprint(evaluaciones_bp, url_prefix="/evaluaciones")
app.register_blueprint(reportes_bp)
app.register_blueprint(cursos_bp, url_prefix="/cursos")
app.register_blueprint(notas_bp, url_prefix="/notas")
app.register_blueprint(asistencia_bp, url_prefix="/asistencia")
app.register_blueprint(alumnos_bp, url_prefix="/alumnos")
app.register_blueprint(equipos_bp, url_prefix="/equipos")




@app.route("/")
def home():
    return "Hola Flask"

if __name__ == "__main__":
    app.run(debug=True, port=os.environ.get("PORT", 5000))
