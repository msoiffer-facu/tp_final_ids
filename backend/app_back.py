from flask import Flask
from routes.profesores import profesores_bp

app = Flask(__name__)
app.register_blueprint(profesores_bp, url_prefix="/profesores")

@app.route("/")
def home():
    return "Hola Flask"

if __name__ == "__main__":
    app.run(debug=True)