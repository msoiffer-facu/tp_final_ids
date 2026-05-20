import os

from flask import Flask
from routes.profesores import profesores_bp
from routes.evaluaciones import evaluaciones_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

app.register_blueprint(profesores_bp, url_prefix="/profesores")
app.register_blueprint(evaluaciones_bp, url_prefix="/evaluaciones")

@app.route("/")
def home():
    return "Hola Flask"

if __name__ == "__main__":
    app.run(debug=True)