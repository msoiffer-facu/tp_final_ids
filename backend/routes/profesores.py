import mysql.connector
from auth import login_required
from db import get_db
from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

profesores_bp = Blueprint("profesores", __name__)


@profesores_bp.route("/login", methods=["POST"])
def login():
    datos = request.get_json()
    email = datos.get("email")
    password = datos.get("password")

    if not email or not password:
        return jsonify({"error": "email y password requeridos"}), 400

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM profesores WHERE email = %s", (email,))
    profesor = cursor.fetchone()
    cursor.close()
    db.close()

    if not profesor or not check_password_hash(profesor["password"], password):
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
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profesores")
        profesores = cursor.fetchall()
        cursor.close()
        db.close()
        return jsonify(profesores), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profesores_bp.route("/<int:profesor_id>", methods=["GET"])
def obtener_profesor(profesor_id):
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM profesores WHERE id = %s", (profesor_id,))
        profesor = cursor.fetchone()
        cursor.close()
        db.close()

        if not profesor:
            return jsonify({"error": "Profesor no encontrado"}), 404
        return jsonify(profesor), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profesores_bp.route("/", methods=["POST"])
@login_required
def crear_profesor():
    try:
        datos = request.get_json()

        if not all([datos.get("nombre"), datos.get("apellido"),
                   datos.get("password"), datos.get("email")]):
            return jsonify({"error": "Faltan campos requeridos"}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO profesores (nombre, apellido, password, email) VALUES (%s, %s, %s, %s)",
            (datos["nombre"], datos["apellido"], generate_password_hash(datos["password"]), datos["email"])
        )
        db.commit()
        profesor_id = cursor.lastrowid
        cursor.close()
        db.close()

        return jsonify({"mensaje": "Profesor creado", "profesor_id": profesor_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El usuario o email ya existe"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profesores_bp.route("/<int:profesor_id>", methods=["PUT"])
@login_required
def actualizar_profesor(profesor_id):
    try:
        datos = request.get_json()
        db = get_db()
        cursor = db.cursor()

        campos = []
        valores = []
        for campo in ["nombre", "apellido", "email"]:
            if campo in datos and datos[campo] is not None:
                campos.append(f"{campo} = %s")
                valores.append(datos[campo])

        if "password" in datos and datos["password"]:
            campos.append("password = %s")
            valores.append(datos["password"])

        if not campos:
            return jsonify({"error": "No hay campos para actualizar"}), 400

        valores.append(profesor_id)
        query = f"UPDATE profesores SET {', '.join(campos)} WHERE id = %s"
        cursor.execute(query, valores)
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Profesor no encontrado"}), 404

        cursor.close()
        db.close()
        return jsonify({"mensaje": "Profesor actualizado"}), 200
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El usuario o email ya existe"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@profesores_bp.route("/<int:profesor_id>", methods=["DELETE"])
@login_required
def eliminar_profesor(profesor_id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM profesores WHERE id = %s", (profesor_id,))
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Profesor no encontrado"}), 404

        cursor.close()
        db.close()
        return jsonify({"mensaje": "Profesor eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
