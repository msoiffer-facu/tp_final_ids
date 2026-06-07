import requests

from services.config import BACKEND_URL


def obtener_cursos(page=1, per_page=100):
    try:
        response = requests.get(f"{BACKEND_URL}/cursos", params={"page": page, "per_page": per_page})
        data = response.json()
        cursos = data.get("cursos", [])
    except:
        cursos = []
    return cursos


def obtener_cursos_paginados(page=1, per_page=10):
    try:
        response = requests.get(f"{BACKEND_URL}/cursos", params={"page": page, "per_page": per_page})
        data = response.json()
    except:
        data = {"cursos": [], "page": page, "total_pages": 1}
    return data


def obtener_curso(id):
    try:
        response = requests.get(f"{BACKEND_URL}/cursos/{id}")
        curso = response.json()
    except:
        curso = None
    return curso


def crear_curso(data):
    try:
        response = requests.post(f"{BACKEND_URL}/cursos", json=data)
        resultado = response.json()
    except:
        resultado = None
    return resultado


def actualizar_curso(id, data):
    try:
        response = requests.put(f"{BACKEND_URL}/cursos/{id}", json=data)
        resultado = response.json()
    except:
        resultado = None
    return resultado


def eliminar_curso(id):
    try:
        response = requests.delete(f"{BACKEND_URL}/cursos/{id}")
        resultado = response.json()
    except:
        resultado = None
    return resultado


def obtener_alumnos_curso(id, page=1, per_page=10):
    try:
        response = requests.get(f"{BACKEND_URL}/cursos/{id}/alumnos", params={"page": page, "per_page": per_page})
        data = response.json()
    except:
        data = {"alumnos": [], "page": page, "total_pages": 1}
    return data


def obtener_equipos_curso(id, page=1, per_page=10):
    try:
        response = requests.get(f"{BACKEND_URL}/cursos/{id}/equipos", params={"page": page, "per_page": per_page})
        data = response.json()
    except:
        data = {"equipos": [], "page": page, "total_pages": 1}
    return data


def obtener_clases_curso(id):
    try:
        response = requests.get(f"{BACKEND_URL}/cursos/{id}/clases")
        clases = response.json()
    except:
        clases = []
    return clases
