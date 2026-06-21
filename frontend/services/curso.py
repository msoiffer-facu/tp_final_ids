import requests

from services.config import BACKEND_URL
from services.login import backend_request


def obtener_cursos():
    try:
        response = backend_request("GET", "/cursos", params={"page": 1, "per_page": -1})

        data = response.json()
        return data.get("cursos", [])

    except Exception:
        return []


def obtener_curso(curso_id):
    try:
        response = backend_request("GET", f"/cursos/{curso_id}")

        if response.ok:
            return response.json()

    except requests.RequestException:
        pass

    return None


def crear_curso(datos):
    response = backend_request("POST", "/cursos", json=datos)

    return {"status_code": response.status_code, "data": response.json()}


def actualizar_curso(curso_id, datos):
    response = backend_request("PUT", f"/cursos/{curso_id}", json=datos)

    return {
        "status_code": response.status_code,
        "data": response.json()
    }


def eliminar_curso(curso_id):
    response = backend_request("DELETE", f"/cursos/{curso_id}")

    try:
        data = response.json()
    except Exception:
        data = {"error": response.text}

    return {"status_code": response.status_code, "data": data}