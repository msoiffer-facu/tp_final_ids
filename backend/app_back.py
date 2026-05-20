from flask import Flask
from routes.reportes import reportes_bp

app = Flask(__name__)
app.register_blueprint(reportes_bp)

@app.route("/")
def home():
    return "Hola Flask"

if __name__ == "__main__":
    app.run(debug=True)