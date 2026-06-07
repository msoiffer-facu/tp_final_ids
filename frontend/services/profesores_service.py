import requests
from flask import session

from services.config import BACKEND_URL


def backend_request(method: str, path: str, **kwargs):
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


def get_profesores(page=1, per_page=10):
    return backend_request("GET", "/profesores", params={"page": page, "per_page": per_page})


def get_profesor(profesor_id):
    return backend_request("GET", f"/profesores/{profesor_id}")


def crear_profesor(datos):
    return backend_request("POST", "/profesores", json=datos)


def actualizar_profesor(profesor_id, datos):
    return backend_request("PUT", f"/profesores/{profesor_id}", json=datos)


def eliminar_profesor(profesor_id):
    return backend_request("DELETE", f"/profesores/{profesor_id}")


def login_profesor(email, password):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/profesores/login",
            json={"email": email, "password": password},
            timeout=5,
        )
    except requests.RequestException:
        return False, "No se pudo conectar con el servidor."

    if resp.status_code != 200:
        try:
            return False, resp.json().get("error", "Credenciales inválidas.")
        except ValueError:
            return False, "Credenciales inválidas."

    return True, {"data": resp.json(), "cookies": resp.cookies.get_dict()}


def logout_profesor():
    cookies = session.get("backend_cookies") or {}
    try:
        resp = requests.post(f"{BACKEND_URL}/profesores/logout", cookies=cookies, timeout=5)
    except requests.RequestException:
        return False, "No se pudo conectar con el servidor."

    if resp.status_code >= 400:
        try:
            return False, resp.json().get("error", resp.text or "Error del backend.")
        except ValueError:
            return False, resp.text or "Error del backend."

    return True, resp.json() if resp.text else {}
