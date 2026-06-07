from services.config import BACKEND_URL
import requests

def obtener_cursos():
    try:
        response = requests.get(
        f"{BACKEND_URL}/cursos",
        params={"page": 1, "per_page": -1}
        )
        data = response.json()
        cursos = data["cursos"]
    except:
        cursos = []
    return cursos

def obtener_curso_con_nombre(nombre):
    try:
        response = requests.get(f"{BACKEND_URL}/asistencia")
        clases_p = response.json()
    except:
        clases_p = []
    return clases_p