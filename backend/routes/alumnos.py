from flask import Blueprint, jsonify, request
from db import get_db
from herramientas.importar_csv import importar_alumnos_csv
from herramientas.validaciones_alumnos import validar_email, validar_convertir_padron, validar_convertir_booleano, validar_convertir_string
import os
import mysql.connector

alumnos_bp = Blueprint("alumnos", __name__)

@alumnos_bp.route("/", methods=["GET"])
def listar_alumnos():
    db = None
    cursor = None

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.*,
                   IFNULL(GROUP_CONCAT(e.nombre ORDER BY e.nombre SEPARATOR ', '), 'Sin equipo') AS equipo
            FROM alumnos a
            LEFT JOIN equipo_alumnos ea ON ea.alumno_id = a.id
            LEFT JOIN equipos e ON e.id = ea.equipo_id
            GROUP BY a.id
        """)
        alumnos = cursor.fetchall()

    except mysql.connector.Error:
        return jsonify({"error": "Error interno al listar alumnos"}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return jsonify(alumnos), 200


@alumnos_bp.route("/importar", methods=["POST"])
def importar_lista():
    file = request.files.get("file")

    if file is None:
        return jsonify({"error": "Archivo faltante"}), 400

    name = file.filename
    extension = os.path.splitext(name)[1].lower()

    if extension != '.csv':
        return jsonify({"error": "Formato invalido"}), 400

    resultado = importar_alumnos_csv(file)

    if "error" in resultado:
        return jsonify({"error": resultado["error"]}), 400

    alumnos = resultado["alumnos"]
    errores = resultado["errores"]
    insertados = 0

    db = None
    cursor = None

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        for alumno in alumnos:
            errores_alumnos = []

            cursor.execute("SELECT email, padron FROM alumnos WHERE email=%s OR padron=%s",
                           (alumno["email"], alumno["padron"]))
            alumno_repeticion = cursor.fetchone()

            if alumno_repeticion:
                if alumno_repeticion["email"] == alumno["email"]:
                    errores_alumnos.append(f"Email {alumno['email']} ya registrado")
                if alumno_repeticion["padron"] == alumno["padron"]:
                    errores_alumnos.append(f"Padron {alumno['padron']} ya registrado")

            if errores_alumnos:
                errores.extend(errores_alumnos)
                continue

            cursor.execute(
                "INSERT INTO alumnos (nombre, apellido, email, padron, abandono, estado) VALUES (%s, %s, %s, %s, %s, %s)",
                (alumno["nombre"], alumno["apellido"], alumno["email"], alumno["padron"], alumno["abandono"], alumno["estado"]))
            insertados += 1
        db.commit()

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return jsonify({
        "errores": errores,
        "insertados": insertados
    }), 200


@alumnos_bp.route("/<int:id>", methods=["GET"])
def obtener_alumno(id):
    db = None
    cursor = None

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alumnos WHERE id=%s", (id,))
        alumno = cursor.fetchone()

        if not alumno:
            return jsonify({"error": "Alumno no encontrado"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return jsonify(alumno), 200


@alumnos_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_alumno(id):
    db = None
    cursor = None

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id FROM alumnos WHERE id=%s", (id,))
        alumno = cursor.fetchone()
        if not alumno:
            return jsonify({"error": "Alumno no encontrado"}), 404

        cursor.execute("DELETE FROM alumnos WHERE id=%s", (id,))
        db.commit()

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return jsonify({"mensaje": "Alumno eliminado"}), 200


@alumnos_bp.route("/<int:id>", methods=["PUT"])
def modificar_alumno(id):
    db = None
    cursor = None

    data = request.get_json()
    if data is None:
        return jsonify({"error": "Body faltante"}), 400

    errores = []

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM alumnos WHERE id=%s", (id,))
        alumno = cursor.fetchone()
        if not alumno:
            return jsonify({"error": "Alumno no encontrado"}), 404

        nombre = validar_convertir_string(data.get("nombre", alumno["nombre"]))
        apellido = validar_convertir_string(data.get("apellido", alumno["apellido"]))
        email = data.get("email", alumno["email"])
        padron = validar_convertir_padron(data.get("padron", alumno["padron"]))
        abandono = validar_convertir_booleano(data.get("abandono", alumno["abandono"]))
        estado = validar_convertir_booleano(data.get("estado", alumno["estado"]))

        if nombre is None:
            errores.append("Nombre invalido")
        if apellido is None:
            errores.append("Apellido invalido")
        if padron is None:
            errores.append("Padron invalido")
        else:
            cursor.execute("SELECT padron FROM alumnos WHERE padron=%s AND id!=%s", (padron, id))
            if cursor.fetchone():
                errores.append("Padron ya registrado")

        if not validar_email(email):
            errores.append("Email invalido")
        else:
            cursor.execute("SELECT email FROM alumnos WHERE email=%s AND id!=%s", (email, id))
            if cursor.fetchone():
                errores.append("Email ya registrado")

        if abandono is None:
            errores.append("Abandono invalido")
        if estado is None:
            errores.append("Estado invalido")

        if errores:
            return jsonify({"errores": errores}), 400

        cursor.execute(
            "UPDATE alumnos SET nombre=%s, apellido=%s, email=%s, padron=%s, abandono=%s, estado=%s WHERE id=%s",
            (nombre, apellido, email, padron, abandono, estado, id))
        db.commit()

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return jsonify({"mensaje": "Alumno modificado"}), 200


@alumnos_bp.route("/", methods=["POST"])
def crear_alumno():
    db = None
    cursor = None

    data = request.get_json()
    if data is None:
        return jsonify({"error": "Body faltante"}), 400

    errores = []

    nombre = validar_convertir_string(data.get("nombre"))
    apellido = validar_convertir_string(data.get("apellido"))
    email = data.get("email")
    padron = validar_convertir_padron(data.get("padron"))
    abandono = validar_convertir_booleano(data.get("abandono", False))
    estado = validar_convertir_booleano(data.get("estado", True))

    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        if nombre is None:
            errores.append("Nombre invalido")
        if apellido is None:
            errores.append("Apellido invalido")
        if padron is None:
            errores.append("Padron invalido")
        else:
            cursor.execute("SELECT * FROM alumnos WHERE padron=%s", (padron,))
            if cursor.fetchone():
                errores.append("Padron ya registrado")

        if not validar_email(email):
            errores.append("Email invalido")
        else:
            cursor.execute("SELECT * FROM alumnos WHERE email=%s", (email,))
            if cursor.fetchone():
                errores.append("Email ya registrado")

        if abandono is None:
            errores.append("Abandono invalido")
        if estado is None:
            errores.append("Estado invalido")

        if errores:
            return jsonify({"errores": errores}), 400

        cursor.execute(
            "INSERT INTO alumnos (nombre, apellido, email, padron, abandono, estado) VALUES (%s, %s, %s, %s, %s, %s)",
            (nombre, apellido, email, padron, abandono, estado)
        )
        db.commit()

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

    return jsonify({"mensaje": "Alumno creado"}), 201
