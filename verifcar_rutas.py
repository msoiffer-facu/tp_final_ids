import os
from flask import Flask

app = Flask(__name__, template_folder='../frontend/templates')

print("Carpeta actual:", os.getcwd())
print("Flask busca templates en:", os.path.abspath(app.template_folder))

archivo_buscado = os.path.join(app.template_folder, 'evaluaciones/evaluaciones.html')
print("¿Existe el archivo?:", os.path.exists(archivo_buscado))