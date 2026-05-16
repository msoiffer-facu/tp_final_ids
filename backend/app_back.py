from flask import Flask
from tp_final_ids.backend.routes.login import *

app = Flask(__name__)

@app.route("/")
def home():
    return "Hola Flask"

if __name__ == "__main__":
    app.run(debug=True)