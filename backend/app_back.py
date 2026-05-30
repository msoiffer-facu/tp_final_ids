import os

from flask import Flask
# from routes.login import *
from routes.asistencia import asistencia_bp
from routes.profesores import profesores_bp
from routes.evaluaciones import evaluaciones_bp
from routes.notas import notas_bp
from routes.reportes import reportes_bp
from routes.alumnos import alumnos_bp
# repetido from routes.cursos import cursos_bp
from routes.equipos import equipos_bp
import sys
from routes.cursos import cursos_bp

base_dir = os.path.abspath(os.path.dirname(__file__))

template_dir = os.path.join(base_dir, '..', 'frontend', 'templates')

static_dir = os.path.join(base_dir, '..', 'frontend', 'static')

app = Flask(__name__, 
            template_folder=template_dir, 
            static_folder=static_dir)
app.secret_key = os.environ.get("SECRET_KEY")

app.register_blueprint(profesores_bp, url_prefix="/profesores")
app.register_blueprint(evaluaciones_bp, url_prefix="/evaluaciones")
app.register_blueprint(reportes_bp)
# repetido app.register_blueprint(cursos_bp, url_prefix="/api")

app.register_blueprint(notas_bp, url_prefix="/notas")
app.register_blueprint(asistencia_bp, url_prefix="/asistencia")
app.register_blueprint(alumnos_bp, url_prefix="/alumnos")
app.register_blueprint(cursos_bp, url_prefix="/cursos", name="cursos_v2")
app.register_blueprint(equipos_bp, url_prefix="/equipos")


@app.route("/")
def home():
    return "Hola Flask"

if __name__ == "__main__":
    app.run(debug=True)
