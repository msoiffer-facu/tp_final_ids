from flask import Flask

from backend.routes.alumnos import *
from backend.routes.asistencia import *
from backend.routes.equipos import *
from backend.routes.login import *
from backend.routes.evaluaciones import *

app = Flask(__name__)

app.register_blueprint(asistencia_bp, url_prefix="/asistencia")
app.register_blueprint(equipos_bp, url_prefix="/equipos")
app.register_blueprint(login_bp, url_prefix="/login")
app.register_blueprint(alumnos_bp, url_prefix="/alumnos")
app.register_blueprint(evaluaciones_bp, url_prefix="/evaluaciones")

if __name__ == "__main__":
    app.run(debug=True)