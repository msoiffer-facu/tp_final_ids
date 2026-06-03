import requests

from services.config import BACKEND_URL


def obtener_cursos():
    try:
        response = requests.get(
            f"{BACKEND_URL}/cursos",
            params={"page": 1, "per_page": 100},
            timeout=5,
        )
        if response.ok:
            return response.json().get("cursos", [])
    except requests.RequestException:
        pass

    return [
        {"id": 1, "nombre": "curso 3b"},
        {"id": 2, "nombre": "curso 4a"},
        {"id": 3, "nombre": "curso 12c"},
        {"id": 4, "nombre": "curso 14l"},
        {"id": 5, "nombre": "curso 1g"},
    ]


def obtener_curso(curso_id):
    try:
        response = requests.get(f"{BACKEND_URL}/cursos/{curso_id}", timeout=5)
        if response.ok:
            return response.json()
    except requests.RequestException:
        pass
    return None
