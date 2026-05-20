from flask import Blueprint, request, jsonify
from db_cursos import get_connection
import mysql.connector

cursos_bp = Blueprint("cursos", __name__)


# ─────────────────────────────────────────
# CURSOS
# ─────────────────────────────────────────

# GET /cursos - listar todos los cursos
@cursos_bp.route("/cursos", methods=["GET"])
def get_cursos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos")
    cursos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(cursos), 200


# GET /cursos/<id> - obtener un curso por ID
@cursos_bp.route("/cursos/<int:id>", methods=["GET"])
def get_curso(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos WHERE id = %s", (id,))
    curso = cursor.fetchone()
    cursor.close()
    conn.close()
    if not curso:
        return jsonify({"error": "Curso no encontrado."}), 404
    return jsonify(curso), 200


# POST /cursos - crear un curso
@cursos_bp.route("/cursos", methods=["POST"])
def create_curso():
    data = request.get_json()
    nombre = data.get("nombre")
    cuatrimestre = data.get("cuatrimestre")
    anio = data.get("anio")
    modificacion = data.get("modificacion")

    if not anio:
        return jsonify({"error": "El campo anio es obligatorio."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cursos (nombre, cuatrimestre, anio, modificacion) VALUES (%s, %s, %s, %s)",
        (nombre, cuatrimestre, anio, modificacion)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Curso creado exitosamente.", "id": nuevo_id}), 201


# PUT /cursos/<id> - actualizar un curso
@cursos_bp.route("/cursos/<int:id>", methods=["PUT"])
def update_curso(id):
    data = request.get_json()
    nombre = data.get("nombre")
    cuatrimestre = data.get("cuatrimestre")
    anio = data.get("anio")
    modificacion = data.get("modificacion")

    if not anio:
        return jsonify({"error": "El campo anio es obligatorio."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cursos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Curso no encontrado."}), 404

    cursor.execute(
        "UPDATE cursos SET nombre = %s, cuatrimestre = %s, anio = %s, modificacion = %s WHERE id = %s",
        (nombre, cuatrimestre, anio, modificacion, id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Curso actualizado exitosamente."}), 200


# DELETE /cursos/<id> - eliminar un curso
@cursos_bp.route("/cursos/<int:id>", methods=["DELETE"])
def delete_curso(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cursos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Curso no encontrado."}), 404

    cursor.execute("DELETE FROM cursos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Curso eliminado exitosamente."}), 200


# ─────────────────────────────────────────
# ALUMNOS DEL CURSO (tabla alumnos_curso)
# ─────────────────────────────────────────

# GET /cursos/<id>/alumnos - listar alumnos inscriptos en un curso
@cursos_bp.route("/cursos/<int:id>/alumnos", methods=["GET"])
def get_alumnos_curso(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM cursos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Curso no encontrado."}), 404

    cursor.execute("""
        SELECT a.id, a.padron, a.nombre, a.apellido, a.email, a.abandono, a.estado
        FROM alumnos_curso ac
        JOIN alumnos a ON ac.alumnos_id = a.id
        WHERE ac.curso_id = %s
        ORDER BY a.apellido, a.nombre
    """, (id,))
    alumnos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(alumnos), 200


# POST /cursos/<id>/alumnos - inscribir un alumno a un curso
@cursos_bp.route("/cursos/<int:id>/alumnos", methods=["POST"])
def inscribir_alumno(id):
    data = request.get_json()
    alumno_id = data.get("alumno_id")
    if not alumno_id:
        return jsonify({"error": "El campo alumno_id es obligatorio."}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cursos WHERE id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Curso no encontrado."}), 404

        cursor.execute(
            "INSERT INTO alumnos_curso (alumnos_id, curso_id) VALUES (%s, %s)",
            (alumno_id, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Alumno inscripto exitosamente."}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El alumno ya está inscripto en este curso."}), 409


# DELETE /cursos/<id>/alumnos/<alumno_id> - desinscribir alumno
@cursos_bp.route("/cursos/<int:id>/alumnos/<int:alumno_id>", methods=["DELETE"])
def desinscribir_alumno(id, alumno_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM alumnos_curso WHERE curso_id = %s AND alumnos_id = %s",
        (id, alumno_id)
    )
    conn.commit()
    afectados = cursor.rowcount
    cursor.close()
    conn.close()
    if afectados == 0:
        return jsonify({"error": "Inscripción no encontrada."}), 404
    return jsonify({"message": "Alumno desinscripto exitosamente."}), 200


# ─────────────────────────────────────────
# CLASES PRESENCIALES (tabla clase_presencial)
# ─────────────────────────────────────────

# GET /cursos/<id>/clases - listar clases de un curso
@cursos_bp.route("/cursos/<int:id>/clases", methods=["GET"])
def get_clases(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clase_presencial WHERE curso_id = %s ORDER BY fecha", (id,))
    clases = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(clases), 200


# POST /cursos/<id>/clases - agregar una clase a un curso
@cursos_bp.route("/cursos/<int:id>/clases", methods=["POST"])
def create_clase(id):
    data = request.get_json()
    fecha = data.get("fecha")

    if not fecha:
        return jsonify({"error": "El campo fecha es obligatorio."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cursos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Curso no encontrado."}), 404

    cursor.execute(
        "INSERT INTO clase_presencial (curso_id, fecha) VALUES (%s, %s)",
        (id, fecha)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Clase creada exitosamente.", "id": nuevo_id}), 201


# DELETE /cursos/<id>/clases/<clase_id> - eliminar una clase
@cursos_bp.route("/cursos/<int:id>/clases/<int:clase_id>", methods=["DELETE"])
def delete_clase(id, clase_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM clase_presencial WHERE id = %s AND curso_id = %s",
        (clase_id, id)
    )
    conn.commit()
    afectados = cursor.rowcount
    cursor.close()
    conn.close()
    if afectados == 0:
        return jsonify({"error": "Clase no encontrada."}), 404
    return jsonify({"message": "Clase eliminada exitosamente."}), 200


# ─────────────────────────────────────────
# EQUIPOS (tabla equipos / equipo_alumnos)
# ─────────────────────────────────────────

# GET /cursos/<id>/equipos - listar equipos de un curso
@cursos_bp.route("/cursos/<int:id>/equipos", methods=["GET"])
def get_equipos(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM equipos WHERE curso_id = %s", (id,))
    equipos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(equipos), 200


# POST /cursos/<id>/equipos - crear un equipo en un curso
@cursos_bp.route("/cursos/<int:id>/equipos", methods=["POST"])
def create_equipo(id):
    data = request.get_json()
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")

    if not nombre:
        return jsonify({"error": "El campo nombre es obligatorio."}), 400

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cursos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Curso no encontrado."}), 404

    cursor.execute(
        "INSERT INTO equipos (nombre, descripcion, curso_id) VALUES (%s, %s, %s)",
        (nombre, descripcion, id)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return jsonify({"message": "Equipo creado exitosamente.", "id": nuevo_id}), 201


# GET /cursos/<id>/equipos/<equipo_id>/alumnos - alumnos de un equipo
@cursos_bp.route("/cursos/<int:id>/equipos/<int:equipo_id>/alumnos", methods=["GET"])
def get_alumnos_equipo(id, equipo_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, a.padron, a.nombre, a.apellido, a.email
        FROM equipo_alumnos ea
        JOIN alumnos a ON ea.alumno_id = a.id
        WHERE ea.equipo_id = %s
        ORDER BY a.apellido, a.nombre
    """, (equipo_id,))
    alumnos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(alumnos), 200


# POST /cursos/<id>/equipos/<equipo_id>/alumnos - agregar alumno a equipo
@cursos_bp.route("/cursos/<int:id>/equipos/<int:equipo_id>/alumnos", methods=["POST"])
def agregar_alumno_equipo(id, equipo_id):
    data = request.get_json()
    alumno_id = data.get("alumno_id")
    if not alumno_id:
        return jsonify({"error": "El campo alumno_id es obligatorio."}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO equipo_alumnos (equipo_id, alumno_id) VALUES (%s, %s)",
            (equipo_id, alumno_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Alumno agregado al equipo exitosamente."}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El alumno ya está en este equipo."}), 409


# DELETE /cursos/<id>/equipos/<equipo_id>/alumnos/<alumno_id> - quitar alumno de equipo
@cursos_bp.route("/cursos/<int:id>/equipos/<int:equipo_id>/alumnos/<int:alumno_id>", methods=["DELETE"])
def quitar_alumno_equipo(id, equipo_id, alumno_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM equipo_alumnos WHERE equipo_id = %s AND alumno_id = %s",
        (equipo_id, alumno_id)
    )
    conn.commit()
    afectados = cursor.rowcount
    cursor.close()
    conn.close()
    if afectados == 0:
        return jsonify({"error": "El alumno no pertenece a este equipo."}), 404
    return jsonify({"message": "Alumno quitado del equipo exitosamente."}), 200
