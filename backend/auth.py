from functools import wraps

from flask import jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash


def hashear_password(password: str) -> str:
    return generate_password_hash(password, method="pbkdf2:sha256")


def verificar_password(password_hasheada: str, password: str) -> bool:
    return check_password_hash(password_hasheada, password)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "profesor_id" not in session:
            return jsonify({"error": "No autenticado"}), 401
        return f(*args, **kwargs)
    return decorated
