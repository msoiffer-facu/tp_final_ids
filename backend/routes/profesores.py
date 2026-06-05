import mysql.connector
from auth import login_required, hashear_password, verificar_password
from flask import Blueprint, jsonify, request, session
from routes.db_profesores import (
    db_get_profesores,
    db_get_profesor_by_id,
    db_get_profesor_by_email,
    db_create_profesor,
    db_update_profesor,
    db_delete_profesor,
)

profesores_bp = Blueprint("profesores", __name__)


@profesores_bp.route("/login", methods=["POST"])
def login():
    datos = request.get_json() or {}
    email = datos.get("email")
    password = datos.get("password")

    if not email or not password:
        return jsonify({"error": "email y password requeridos"}), 400

    try:
        profesor = db_get_profesor_by_email(email)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if not profesor or not verificar_password(profesor["password"], password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    session["profesor_id"] = profesor["id"]
    session["email"] = profesor["email"]
    return jsonify({"mensaje": "Login exitoso", "profesor_id": profesor["id"]}), 200


@profesores_bp.route("/crear-test", methods=["GET"])
def crear_profesor_test():
    """RUTA TEMPORAL PARA PRUEBAS - borrar antes de entregar"""
    try:
        profesor_id = db_create_profesor("Admin", "Test", "admin@test.com", hashear_password("1234"))
        return jsonify({"mensaje": "Profesor de prueba creado", "email": "admin@test.com", "password": "1234", "id": profesor_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"mensaje": "Ya existe, usá email: admin@test.com  password: 1234"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profesores_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensaje": "Logout exitoso"}), 200


@profesores_bp.route("/", methods=["GET"])
def listar_profesores():
    try:
        profesores = db_get_profesores()
        return jsonify(profesores), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profesores_bp.route("/<int:profesor_id>", methods=["GET"])
def obtener_profesor(profesor_id):
    try:
        profesor = db_get_profesor_by_id(profesor_id)
        if not profesor:
            return jsonify({"error": "Profesor no encontrado"}), 404
        return jsonify(profesor), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profesores_bp.route("/", methods=["POST"])
# @login_required
def crear_profesor():
    datos = request.get_json() or {}
    nombre = datos.get("nombre")
    apellido = datos.get("apellido")
    email = datos.get("email")
    password = datos.get("password")

    if not nombre:
        return jsonify({"error": "El campo nombre es obligatorio"}), 400
    if not apellido:
        return jsonify({"error": "El campo apellido es obligatorio"}), 400
    if not email:
        return jsonify({"error": "El campo email es obligatorio"}), 400
    if not password:
        return jsonify({"error": "El campo password es obligatorio"}), 400

    try:
        profesor_id = db_create_profesor(nombre, apellido, email, hashear_password(password))
        return jsonify({"mensaje": "Profesor creado", "profesor_id": profesor_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El usuario o email ya existe"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profesores_bp.route("/<int:profesor_id>", methods=["PUT"])
@login_required
def actualizar_profesor(profesor_id):
    try:
        profesor_existente = db_get_profesor_by_id(profesor_id)
        if not profesor_existente:
            return jsonify({"error": "Profesor no encontrado"}), 404

        datos = request.get_json() or {}
        nombre = datos.get("nombre")
        apellido = datos.get("apellido")
        email = datos.get("email")
        password = datos.get("password")

        if nombre is not None and nombre == "":
            return jsonify({"error": "El campo nombre no puede estar vacío"}), 400
        if apellido is not None and apellido == "":
            return jsonify({"error": "El campo apellido no puede estar vacío"}), 400
        if email is not None and email == "":
            return jsonify({"error": "El campo email no puede estar vacío"}), 400
        if password is not None and password == "":
            return jsonify({"error": "El campo password no puede estar vacío"}), 400

        if nombre is None and apellido is None and email is None and password is None:
            return jsonify({"error": "No hay campos para actualizar"}), 400

        db_update_profesor(
            profesor_id,
            nombre=nombre,
            apellido=apellido,
            email=email,
            password=hashear_password(password) if password is not None else None,
        )
        return jsonify({"mensaje": "Profesor actualizado"}), 200
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El usuario o email ya existe"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profesores_bp.route("/<int:profesor_id>", methods=["DELETE"])
@login_required
def eliminar_profesor(profesor_id):
    try:
        afectados = db_delete_profesor(profesor_id)
        if afectados == 0:
            return jsonify({"error": "Profesor no encontrado"}), 404
        return jsonify({"mensaje": "Profesor eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
