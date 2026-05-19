import os
from functools import wraps
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()

def requiere_token(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Token no proporcionado."}), 401
        if token != f"Bearer {os.getenv('API_TOKEN')}":
            return jsonify({"error": "Token inválido."}), 403
        return f(*args, **kwargs)
    return decorador
