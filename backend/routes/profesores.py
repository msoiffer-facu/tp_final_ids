import mysql.connector
from auth import login_required, hashear_password, verificar_password
from flask import Blueprint, jsonify, request, session
from dbs.db_profesores import (
    db_get_profesores,
    db_get_profesor_by_id,
    db_get_profesor_by_email,
    db_create_profesor,
    db_update_profesor,
    db_delete_profesor,
)

from dbs.db_historial import registrar_historial_profesores
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



@profesores_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"mensaje": "Logout exitoso"}), 200


@profesores_bp.route("/", methods=["GET"])
def listar_profesores():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        profesores, total = db_get_profesores(page, per_page)
        return jsonify({
            "profesores": profesores,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }), 200
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
        # verificar email existente antes de intentar insertar (por si la BD no tiene constraint aplicable)
        existente = db_get_profesor_by_email(email)
        if existente:
            return jsonify({"error": "El email ya está en uso por otro profesor"}), 409
        profesor_id = db_create_profesor(nombre, apellido, email, hashear_password(password))

        registrar_historial_profesores(f"Agregó al profesor {nombre} {apellido}", session.get("email"))

        return jsonify({"mensaje": "Profesor creado", "profesor_id": profesor_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El email ya está en uso por otro profesor"}), 409
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

        # si se proporciona email, verificar que no esté en uso por otro profesor
        if email is not None:
            existente = db_get_profesor_by_email(email)
            if existente and existente.get("id") != profesor_id:
                return jsonify({"error": "El email ya está en uso por otro profesor"}), 409

        db_update_profesor(
            profesor_id,
            nombre=nombre,
            apellido=apellido,
            email=email,
            password=hashear_password(password) if password is not None else None,
        )

        registrar_historial_profesores(f"Modificó al profesor {profesor_existente['nombre']} {profesor_existente['apellido']}", session.get("email"))

        return jsonify({"mensaje": "Profesor actualizado"}), 200
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El email ya está en uso por otro profesor"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profesores_bp.route("/<int:profesor_id>", methods=["DELETE"])
@login_required
def eliminar_profesor(profesor_id):
    try:
        profesor = db_get_profesor_by_id(profesor_id)
        
        if not profesor:
            return jsonify({"error": "Profesor no encontrado"}), 404
        
        afectados = db_delete_profesor(profesor_id)
        if afectados == 0:
            return jsonify({"error": "Profesor no encontrado"}), 404
        
        registrar_historial_profesores(f"Eliminó al profesor {profesor['nombre']} {profesor['apellido']}", session.get("email"))
        
        return jsonify({"mensaje": "Profesor eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
