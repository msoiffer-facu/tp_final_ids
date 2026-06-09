import requests

from services.config import BACKEND_URL
from services.login import backend_request


def _parse_response(resp):
    if resp.status_code == 204:
        return {}

    try:
        data = resp.json()
    except ValueError:
        data = {}

    if not resp.ok:
        raise RuntimeError(data.get("error", f"Error {resp.status_code} al comunicarse con el backend."))

    return data


def obtener_equipos():
    resp = backend_request("GET", "/equipos", timeout=5)
    return _parse_response(resp)


def obtener_equipo(equipo_id):
    resp = backend_request("GET", f"/equipos/{equipo_id}", timeout=5)
    return _parse_response(resp)


def crear_equipo(nombre, descripcion, curso_id):
    resp = backend_request(
        "POST",
        "/equipos",
        json={"nombre": nombre, "descripcion": descripcion, "curso_id": curso_id},
        timeout=5,
    )
    return _parse_response(resp)


def editar_equipo(equipo_id, nombre, descripcion):
    resp = backend_request(
        "PUT",
        f"/equipos/{equipo_id}",
        json={"nombre": nombre, "descripcion": descripcion},
        timeout=5,
    )
    return _parse_response(resp)


def eliminar_equipo(equipo_id):
    resp = backend_request("DELETE", f"/equipos/{equipo_id}", timeout=5)
    return _parse_response(resp)


def agregar_alumno_equipo(equipo_id, alumno_id):
    resp = backend_request(
        "POST",
        f"/equipos/{equipo_id}/alumnos",
        json={"alumnos": [alumno_id]},
        timeout=5,
    )
    return _parse_response(resp)


def quitar_alumno_equipo(equipo_id, alumno_id):
    resp = backend_request(
        "DELETE",
        f"/equipos/{equipo_id}/alumnos/{alumno_id}",
        timeout=5,
    )
    return _parse_response(resp)


def obtener_miembros_equipo(curso_id, equipo_id):
    resp = backend_request(
        "GET",
        f"/cursos/{curso_id}/equipos/{equipo_id}/alumnos",
        timeout=5,
    )
    return _parse_response(resp)


def obtener_evaluaciones_equipo(equipo_id):
    resp = backend_request("GET", f"/equipos/{equipo_id}/evaluaciones", timeout=5)
    return _parse_response(resp)


def asociar_equipo_evaluacion(equipo_id, evaluacion_id):
    resp = backend_request(
        "POST",
        f"/equipos/{equipo_id}/tps",
        json={"evaluacion_id": evaluacion_id},
        timeout=5,
    )
    return _parse_response(resp)
