from flask import Flask
from tp_final_ids.backend.routes.login import *
from tp_final_ids.backend.routes.cursada import cursada_bp

app = Flask(__name__)

app.register_blueprint(asistencia_bp, url_prefix="/asistencia")


@app.route("/")
def home():
    return "Hola Flask"

if __name__ == "__main__":
    app.run(debug=True)