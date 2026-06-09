import requests

from services.config import BACKEND_URL


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


def obtener_curso(curso_id):
    try:
        response = requests.get(f"{BACKEND_URL}/cursos/{curso_id}", timeout=5)
        if response.ok:
            return response.json()
    except requests.RequestException:
        pass
    return None
