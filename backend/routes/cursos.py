from flask import Blueprint, request, jsonify
import mysql.connector
from dbs.db_cursos import (
    db_get_cursos, db_get_curso_by_id, db_create_curso, db_update_curso, db_delete_curso,
    db_get_alumnos_curso, db_inscribir_alumno, db_desinscribir_alumno,
    db_get_clases, db_create_clase, db_delete_clase,
    db_get_equipos, db_create_equipo,
    db_get_alumnos_equipo, db_agregar_alumno_equipo, db_quitar_alumno_equipo
)

cursos_bp = Blueprint("cursos", __name__)



@cursos_bp.route("/", methods=["GET"])
def get_cursos():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        cursos, total = db_get_cursos(page, per_page)  # ← cambia la firma
    except:
        return jsonify({"error": "error en el servidor"}), 500
    return jsonify({
        "cursos": cursos,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page
    }), 200

@cursos_bp.route("/<int:id>", methods=["GET"])
def get_curso(id):
    try:
        curso = db_get_curso_by_id(id)
        if not curso:
            return jsonify({"error": "Curso no encontrado."}), 404
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify(curso), 200


@cursos_bp.route("/", methods=["POST"])
def create_curso():
    data = request.get_json()
    nombre = data.get("nombre")
    cuatrimestre = data.get("cuatrimestre")
    anio = data.get("anio")
    modificacion = data.get("modificacion")

    try:
        if not nombre:
            return jsonify({"error": "El campo nombre es obligatorio."}), 400
        if not anio:
            return jsonify({"error": "El campo anio es obligatorio."}), 400
        if not cuatrimestre or cuatrimestre not in ["1", "2"]:
            return jsonify({"error": "El campo cuatrimestre es obligatorio y debe ser '1' o '2'."}), 400

        nuevo_id = db_create_curso(nombre, cuatrimestre, anio, modificacion)
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify({"message": "Curso creado exitosamente.", "id": nuevo_id}), 201

@cursos_bp.route("/cursos/<int:id>", methods=["PUT"])
def update_curso(id):
    if not db_get_curso_by_id(id):
        return jsonify({"error": "Curso no encontrado."}), 404

    data = request.get_json()
    nombre = data.get("nombre")
    cuatrimestre = data.get("cuatrimestre")
    anio = data.get("anio")
    modificacion = data.get("modificacion")

    try:
        if not nombre:
            return jsonify({"error": "El campo nombre es obligatorio."}), 400
        if not anio:
            return jsonify({"error": "El campo anio es obligatorio."}), 400
        if not cuatrimestre or cuatrimestre not in ["1", "2"]:
            return jsonify({"error": "El campo cuatrimestre es obligatorio y debe ser '1' o '2'."}), 400

        db_update_curso(id, nombre, cuatrimestre, anio, modificacion)
    except:
        return jsonify({"message": "Curso creado exitosamente.", "id": nuevo_id}), 201
    return jsonify({"message": "Curso actualizado exitosamente."}), 200


@cursos_bp.route("/<int:id>", methods=["DELETE"])
def delete_curso(id):
    try:
        if not db_get_curso_by_id(id):
            return jsonify({"error": "Curso no encontrado."}), 404
        db_delete_curso(id)
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify({"message": "Curso eliminado exitosamente."}), 200


# ─── ALUMNOS DEL CURSO ───

@cursos_bp.route("/cursos/<int:id>/alumnos", methods=["GET"])
def get_alumnos_curso(id):
    try:
        if not db_get_curso_by_id(id):
            return jsonify({"error": "Curso no encontrado."}), 404
        alumnos = db_get_alumnos_curso(id)
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify(alumnos), 200


@cursos_bp.route("/<int:id>/alumnos", methods=["POST"])
def inscribir_alumno(id):

    if not db_get_curso_by_id(id):
        return jsonify({"error": "Curso no encontrado."}), 404

    data = request.get_json()
    alumno_id = data.get("alumno_id")

    # Validaciones
    if not alumno_id:
        return jsonify({"error": "El campo alumno_id es obligatorio."}), 400

    try:
        db_inscribir_alumno(id, alumno_id)
        return jsonify({"message": "Alumno inscripto exitosamente."}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El alumno ya está inscripto en este curso."}), 409
    except:
        return  jsonify({"error": "error en el servidor"}), 500


@cursos_bp.route("/<int:id>/alumnos/<int:alumno_id>", methods=["DELETE"])
def desinscribir_alumno(id, alumno_id):
    try:
        if not db_get_curso_by_id(id):
            return jsonify({"error": "Curso no encontrado."}), 404
        afectados = db_desinscribir_alumno(id, alumno_id)
        if afectados == 0:
            return jsonify({"error": "Inscripción no encontrada."}), 404
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify({"message": "Alumno desinscripto exitosamente."}), 200


# ─── CLASES PRESENCIALES ───

@cursos_bp.route("/<int:id>/clases", methods=["GET"])
def get_clases(id):
    try:
        if not db_get_curso_by_id(id):
            return jsonify({"error": "Curso no encontrado."}), 404
        clases = db_get_clases(id)
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify(clases), 200


@cursos_bp.route("/<int:id>/clases", methods=["POST"])
def create_clase(id):
    try:
        
        if not db_get_curso_by_id(id):
            return jsonify({"error": "Curso no encontrado."}), 404

        data = request.get_json()
        fecha = data.get("fecha")

        # Validaciones
        if not fecha:
            return jsonify({"error": "El campo fecha es obligatorio."}), 400

        nuevo_id = db_create_clase(id, fecha)
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify({"message": "Clase creada exitosamente.", "id": nuevo_id}), 201


@cursos_bp.route("/<int:id>/clases/<int:clase_id>", methods=["DELETE"])
def delete_clase(id, clase_id):
    try:
        if not db_get_curso_by_id(id):
            return jsonify({"error": "Curso no encontrado."}), 404
        afectados = db_delete_clase(clase_id, id)
        if afectados == 0:
            return jsonify({"error": "Clase no encontrada."}), 404
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify({"message": "Clase eliminada exitosamente."}), 200


# ─── EQUIPOS ───

@cursos_bp.route("/<int:id>/equipos", methods=["GET"])
def get_equipos(id):
    try:
        if not db_get_curso_by_id(id):
            return jsonify({"error": "Curso no encontrado."}), 404
        equipos = db_get_equipos(id)
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify(equipos), 200


@cursos_bp.route("/<int:id>/equipos", methods=["POST"])
def create_equipo(id):
    try:
        if not db_get_curso_by_id(id):
            return jsonify({"error": "Curso no encontrado."}), 404

        data = request.get_json()
        nombre = data.get("nombre")
        descripcion = data.get("descripcion")

        # Validaciones
        if not nombre:
            return jsonify({"error": "El campo nombre es obligatorio."}), 400

        nuevo_id = db_create_equipo(nombre, descripcion, id)
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify({"message": "Equipo creado exitosamente.", "id": nuevo_id}), 201


@cursos_bp.route("/<int:id>/equipos/<int:equipo_id>/alumnos", methods=["GET"])
def get_alumnos_equipo(id, equipo_id):
    try:
        alumnos = db_get_alumnos_equipo(equipo_id)
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify(alumnos), 200


@cursos_bp.route("/<int:id>/equipos/<int:equipo_id>/alumnos", methods=["POST"])
def agregar_alumno_equipo(id, equipo_id):
    data = request.get_json()
    alumno_id = data.get("alumno_id")

    # Validaciones
    if not alumno_id:
        return jsonify({"error": "El campo alumno_id es obligatorio."}), 400

    try:
        db_agregar_alumno_equipo(equipo_id, alumno_id)
        return jsonify({"message": "Alumno agregado al equipo exitosamente."}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "El alumno ya está en este equipo."}), 409


@cursos_bp.route("/<int:id>/equipos/<int:equipo_id>/alumnos/<int:alumno_id>", methods=["DELETE"])
def quitar_alumno_equipo(id, equipo_id, alumno_id):
    try:
        afectados = db_quitar_alumno_equipo(equipo_id, alumno_id)
        if afectados == 0:
            return jsonify({"error": "El alumno no pertenece a este equipo."}), 404
    except:
        return  jsonify({"error": "error en el servidor"}), 500
    return jsonify({"message": "Alumno quitado del equipo exitosamente."}), 200
