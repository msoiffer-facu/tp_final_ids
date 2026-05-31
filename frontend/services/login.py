import requests
from flask import session

from services.config import BACKEND_URL


def usuario_logueado():
    return session.get("user") is not None


def guardar_sesion(usuario, backend_cookies):
    session["user"] = usuario
    session["backend_cookies"] = backend_cookies


def limpiar_sesion():
    session.pop("user", None)
    session.pop("backend_cookies", None)


def autenticar(email, password):
    """Autentica contra el backend. Devuelve (ok, usuario) o (False, mensaje_error)."""

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

    profesor_id = resp.json().get("profesor_id")
    cookies = resp.cookies.get_dict()

    nombre = email
    try:
        detalle = requests.get(f"{BACKEND_URL}/profesores/{profesor_id}", timeout=5)
        if detalle.ok:
            nombre = detalle.json().get("nombre") or email
    except requests.RequestException:
        pass

    usuario = {"profesor_id": profesor_id, "email": email, "name": nombre}
    return True, (usuario, cookies)


def cerrar_sesion_backend():
    """Cierra la sesión en el backend reenviando la cookie guardada."""
    cookies = session.get("backend_cookies")
    if not cookies:
        return
    try:
        requests.post(f"{BACKEND_URL}/profesores/logout", cookies=cookies, timeout=5)
    except requests.RequestException:
        pass


def backend_request(method: str, path: str, **kwargs):
    """Realiza una petición autenticada al backend reenviando la cookie de sesión."""
    cookies = session.get("backend_cookies") or {}
    return requests.request(method, f"{BACKEND_URL}{path}", cookies=cookies, **kwargs)
