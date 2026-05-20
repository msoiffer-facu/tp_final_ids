from flask import Blueprint, jsonify, request
from backend.db import get_db_connection
from backend.herramientas.importar_csv import importar_alumnos_csv
import os, mysql.connector

alumnos_bp = Blueprint("alumnos", __name__)

@alumnos_bp.route("/importar", methods=["POST"])
def post_lista():
    file=request.files.get("file")
    if file is None:
        return jsonify({"error": "Archivo faltante"}), 400

    name=file.filename
    extension=os.path.splitext(name)[1].lower()

    if extension !='.csv':
        return jsonify({"error": "Formato invalido"}), 400

    resultado = importar_alumnos_csv(file)

    if "error" in resultado:
        return jsonify({"error": resultado["error"]}), 400

    alumnos = resultado["alumnos"]
    errores = resultado["errores"]
    insertados = 0

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        for alumno in alumnos:
            cursor.execute("SELECT * FROM alumnos WHERE email=%s", (alumno["email"],))
            alumno_email = cursor.fetchone()
            if alumno_email:
                errores.append(f"Padron {alumno['padron']}: email ya registrado")
                continue

            cursor.execute("SELECT * FROM alumnos WHERE padron=%s", (alumno["padron"],))
            alumno_padron = cursor.fetchone()
            if alumno_padron:
                errores.append(f"Padron {alumno['padron']}: padron ya registrado")
                continue

            cursor.execute(
                "INSERT INTO alumnos (nombre, apellido, email, padron, abandono, estado) VALUES (%s, %s, %s, %s, %s, %s)",
                (alumno["nombre"], alumno["apellido"], alumno["email"], alumno["padron"], alumno["abandono"], alumno["estado"]))
            insertados += 1

        db.commit()
        cursor.close()
        db.close()

    except Exception as err:
        return jsonify({"error": str(err)}), 500

    return jsonify({
        "errores": errores,
        "insertados": insertados
    }), 200


@alumnos_bp.route("/", methods=["GET"])
def get_alumnos():

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alumnos")
        alumnos = cursor.fetchall()
        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    return jsonify(alumnos), 200


@alumnos_bp.route("/<int:id>", methods=["GET"])
def get_alumno(id):
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM alumnos WHERE id=%s",(id,))
        alumno = cursor.fetchone()
        cursor.close()
        db.close()

        if not alumno:
            return jsonify({"error": "Alumno no encontrado"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    return jsonify(alumno), 200


@alumnos_bp.route("/<int:id>", methods=["DELETE"])
def delete_alumno(id):

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM alumnos WHERE id=%s",(id,))
        alumno = cursor.fetchone()
        if not alumno:
            cursor.close()
            db.close()
            return jsonify({"error": "Alumno no encontrado"}), 404

        cursor.execute("DELETE FROM alumnos WHERE id=%s", (id,))
        db.commit()
        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    return jsonify({"mensaje": "Alumno eliminado"}), 200


@alumnos_bp.route("/<int:id>", methods=["PUT"])
def put_alumno(id):
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Body faltante"}), 400

    errores = []

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM alumnos WHERE id=%s", (id,))
        alumno = cursor.fetchone()
        if not alumno:
            cursor.close()
            db.close()
            return jsonify({"error": "Alumno no encontrado"}), 404

        nombre = data.get("nombre", alumno["nombre"])
        apellido = data.get("apellido", alumno["apellido"])
        email = data.get("email", alumno["email"])
        padron = data.get("padron", alumno["padron"])
        abandono = data.get("abandono", alumno["abandono"])
        estado = data.get("estado", alumno["estado"])

        if padron is None:
            cursor.close()
            db.close()
            return jsonify({"error": "Padron obligatorio"}), 400

        try:
            padron = int(padron)

        except (ValueError, TypeError):
            errores.append("Padron invalido")

        cursor.execute("SELECT * FROM alumnos WHERE email=%s AND id!=%s", (email, id))
        alumno_email = cursor.fetchone()
        if alumno_email:
            errores.append("Email ya registrado")

        cursor.execute("SELECT * FROM alumnos WHERE padron=%s AND id!=%s", (padron, id))
        alumno_padron = cursor.fetchone()
        if alumno_padron:
            errores.append("Padron ya registrado")

        if errores:
            cursor.close()
            db.close()
            return jsonify({"errores": errores}), 400

        cursor.execute("UPDATE alumnos SET nombre=%s, apellido=%s, email=%s, padron=%s, abandono=%s, estado=%s WHERE id=%s",
            (nombre,apellido,email,padron,abandono,estado,id))
        db.commit()
        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    return jsonify({"mensaje": "Alumno modificado"}), 200


@alumnos_bp.route("/", methods=["POST"])
def post_alumno():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Body faltante"}), 400

    errores = []

    nombre = data.get("nombre")
    apellido = data.get("apellido")
    email = data.get("email")
    padron = data.get("padron")
    abandono = data.get("abandono", False)
    estado = data.get("estado", True)

    if not nombre:
        errores.append("Nombre obligatorio")
    if not apellido:
        errores.append("Apellido obligatorio")
    if not email:
        errores.append("Email obligatorio")
    if padron is None:
        errores.append("Padron obligatorio")

    try:
        padron = int(padron)

    except (ValueError, TypeError):
        errores.append("Padron invalido")

    if errores:
        return jsonify({"errores": errores}), 400

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM alumnos WHERE email=%s", (email,))
        alumno_email = cursor.fetchone()
        if alumno_email:
            errores.append("Email ya registrado")
        
        cursor.execute("SELECT * FROM alumnos WHERE padron=%s", (padron,))
        alumno_padron = cursor.fetchone()
        if alumno_padron:
            errores.append("Padron ya registrado")

        if errores:
            cursor.close()
            db.close()
            return jsonify({"errores": errores}), 409

        cursor.execute(
            "INSERT INTO alumnos (nombre, apellido, email, padron, abandono, estado) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre, apellido, email, padron, abandono, estado)
        )
        db.commit()
        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    return jsonify({"mensaje": "Alumno creado"}), 201