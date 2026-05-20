from flask import Flask
from backend.routes.alumnos import alumnos_bp

app = Flask(__name__)
app.register_blueprint(alumnos_bp, url_prefix="/alumnos")

@app.route("/")
def home():
    return "Hola Flask"

if __name__ == "__main__":
    app.run(debug=True)