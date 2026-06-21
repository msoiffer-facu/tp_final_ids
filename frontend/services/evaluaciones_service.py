import requests
from flask import session
from services.config import BACKEND_URL


def _req(method, path, **kwargs):
    cookies = session.get("backend_cookies") or {}
    try:
        resp = requests.request(method, f"{BACKEND_URL}{path}", cookies=cookies, timeout=5, **kwargs)
    except requests.RequestException:
        return False, "No se pudo conectar con el servidor."

    if resp.status_code >= 400:
        try:
            return False, resp.json().get("error", resp.text or "Error del backend.")
        except ValueError:
            return False, resp.text or "Error del backend."

    try:
        return True, resp.json()
    except ValueError:
        return True, resp.text


def get_evaluaciones(page=1, per_page=10, tipo_id=None, curso_id=None):
    params = {"page": page, "per_page": per_page}
    if tipo_id:
        params["tipo_id"] = tipo_id
    if curso_id:
        params["curso_id"] = curso_id
    return _req("GET", "/evaluaciones/", params=params)


def get_evaluacion(evaluacion_id):
    return _req("GET", f"/evaluaciones/{evaluacion_id}")


def crear_evaluacion(datos):
    return _req("POST", "/evaluaciones/", json=datos)


def actualizar_evaluacion(evaluacion_id, datos):
    return _req("PUT", f"/evaluaciones/{evaluacion_id}", json=datos)


def eliminar_evaluacion(evaluacion_id):
    return _req("DELETE", f"/evaluaciones/{evaluacion_id}")


def get_tipos():
    return _req("GET", "/evaluaciones/tipos")


def get_tipo(tipo_id):
    return _req("GET", f"/evaluaciones/tipos/{tipo_id}")


def crear_tipo(datos):
    return _req("POST", "/evaluaciones/tipos", json=datos)


def actualizar_tipo(tipo_id, datos):
    return _req("PUT", f"/evaluaciones/tipos/{tipo_id}", json=datos)


def eliminar_tipo(tipo_id):
    return _req("DELETE", f"/evaluaciones/tipos/{tipo_id}")


def get_notas_evaluacion(evaluacion_id):
    return _req("GET", f"/evaluaciones/{evaluacion_id}/notas")


def guardar_notas_evaluacion(evaluacion_id, notas):
    return _req("POST", f"/evaluaciones/{evaluacion_id}/notas", json={"notas": notas})
