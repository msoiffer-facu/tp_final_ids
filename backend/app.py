from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_connection
from auth import requiere_token
import mysql.connector

app = Flask(__name__)
CORS(app)

# ─────────────────────────────────────────
# CURSOS
# ─────────────────────────────────────────

@app.route("/api/cursos", methods=["GET"])
@requiere_token
def get_cursos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, CONCAT(p.nombre, ' ', p.apellido) AS profesor_nombre
        FROM cursos c
        LEFT JOIN profesores p ON c.id_profesor = p.id
        WHERE c.activo = 1
        ORDER BY c.anio DESC, c.cuatrimestre DESC
    """)
    cursos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(cursos), 200


@app.route("/api/cursos/<int:id>", methods=["GET"])
@requiere_token
def get_curso(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.*, CONCAT(p.nombre, ' ', p.apellido) AS profesor_nombre
        FROM cursos c
        LEFT JOIN profesores p ON c.id_profesor = p.id
        WHERE c.id = %s AND c.activo = 1
    """, (id,))
    curso = cursor.fetchone()
    cursor.close()
    conn.close()
    if not curso:
        return jsonify({"error": "Curso no encontrado."}), 404
    return jsonify(curso), 200


@app.route("/api/cursos", methods=["POST"])
@requiere_token
def create_curso():
    data = request.get_json()
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    codigo = data.get("codigo")
    anio = data.get("anio")
    cuatrimestre = data.get("cuatrimestre")
    id_profesor = data.get("id_profesor")

    if not nombre or not codigo or not anio or not cuatrimestre:
        return jsonify({"error": "Campos obligatorios: nombre, codigo, anio, cuatrimestre."}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cursos (nombre, descripcion, codigo, anio, cuatrimestre, id_profesor)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, descripcion, codigo, anio, cuatrimestre, id_profesor))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "Curso creado exitosamente.", "id": nuevo_id}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Ya existe un curso con ese código."}), 409


@app.route("/api/cursos/<int:id>", methods=["PUT"])
@requiere_token
def update_curso(id):
    data = request.get_json()
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    codigo = data.get("codigo")
    anio = data.get("anio")
    cuatrimestre = data.get("cuatrimestre")
    id_profesor = data.get("id_profesor")

    if not nombre or not codigo or not anio or not cuatrimestre:
        return jsonify({"error": "Campos obligatorios: nombre, codigo, anio, cuatrimestre."}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cursos WHERE id = %s AND activo = 1", (id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Curso no encontrado."}), 404

        cursor.execute("""
            UPDATE cursos
            SET nombre = %s, descripcion = %s, codigo = %s,
                anio = %s, cuatrimestre = %s, id_profesor = %s
            WHERE id = %s
        """, (nombre, descripcion, codigo, anio, cuatrimestre, id_profesor, id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Curso actualizado exitosamente."}), 200
    except mysql.connector.IntegrityError:
        return jsonify({"error": "Ya existe un curso con ese código."}), 409


@app.route("/api/cursos/<int:id>", methods=["DELETE"])
@requiere_token
def delete_curso(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cursos WHERE id = %s AND activo = 1", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Curso no encontrado."}), 404

    cursor.execute("UPDATE cursos SET activo = 0 WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Curso eliminado exitosamente."}), 200


# ─────────────────────────────────────────
# INSCRIPCIONES
# ─────────────────────────────────────────

@app.route("/api/cursos/<int:id>/alumnos", methods=["GET"])
@requiere_token
def get_alumnos_curso(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM cursos WHERE id = %s AND activo = 1", (id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"error": "Curso no encontrado."}), 404

    cursor.execute("""
        SELECT a.id, a.nombre, a.apellido, a.legajo, a.email, a.abandono,
               i.fecha_inscripcion
        FROM inscripciones i
        JOIN alumnos a ON i.id_alumno = a.id
        WHERE i.id_curso = %s
        ORDER BY a.apellido, a.nombre
    """, (id,))
    alumnos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(alumnos), 200


@app.route("/api/cursos/<int:id>/alumnos", methods=["POST"])
@requiere_token
def inscribir_alumno(id):
    data = request.get_json()
    id_alumno = data.get("id_alumno")
    if not id_alumno:
        return jsonify({"error": "El campo id_alumno es obligatorio."}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cursos WHERE id = %s AND activo = 1", (id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"error": "Curso no encontrado."}), 404

        cursor.execute(
            "INSERT INTO inscripciones (id_alumno, id_curso) VALUES (%s, %s)",
            (id_alumno, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Alumno inscripto exitosamente."}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El alumno ya está inscripto en este curso."}), 409


@app.route("/api/cursos/<int:id>/alumnos/<int:id_alumno>", methods=["DELETE"])
@requiere_token
def desinscribir_alumno(id, id_alumno):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM inscripciones WHERE id_curso = %s AND id_alumno = %s",
        (id, id_alumno)
    )
    conn.commit()
    afectados = cursor.rowcount
    cursor.close()
    conn.close()
    if afectados == 0:
        return jsonify({"error": "Inscripción no encontrada."}), 404
    return jsonify({"message": "Alumno desinscripto exitosamente."}), 200


# ─────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
