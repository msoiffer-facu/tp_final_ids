from flask import Blueprint, jsonify, request
from dbs.db_equipos import (
    db_listar_equipos,
    db_crear_equipo,
    db_buscar_equipo_por_id,
    db_editar_equipo,
    db_eliminar_equipo,
    db_asociar_alumnos,
    db_quitar_alumno_equipo,
    db_listar_alumnos_equipo,
    db_asociar_equipo_a_tp,
)

equipos_bp = Blueprint("equipos", __name__)


@equipos_bp.route("/", methods=["GET"])
def listar_equipos():
    try:
        equipos = db_listar_equipos()
    except Exception as e:
        return jsonify({"error": f"Error al listar equipos: {str(e)}"}), 500
    return jsonify(equipos), 200


@equipos_bp.route("/", methods=["POST"])
def crear_equipo():
    data = request.get_json()
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    curso_id = data.get("curso_id")

    if not nombre or not curso_id:
        return jsonify({"error": "Faltan campos obligatorios: nombre y curso_id"}), 400

    try:
        nuevo_id = db_crear_equipo(nombre, descripcion, curso_id)
    except Exception as e:
        return jsonify({"error": f"Error al crear el equipo: {str(e)}"}), 500
    return jsonify({"message": "Equipo creado con éxito", "id": nuevo_id}), 201


@equipos_bp.route("/<int:id>", methods=["GET"])
def obtener_equipo(id):
    try:
        equipo = db_buscar_equipo_por_id(id)
    except Exception as e:
        return jsonify({"error": f"Error al obtener equipo: {str(e)}"}), 500
    if not equipo:
        return jsonify({"error": "Equipo no encontrado"}), 404
    return jsonify(equipo), 200


@equipos_bp.route("/<int:id>", methods=["PUT"])
def editar_equipo(id):
    data = request.get_json()
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")

    if not nombre:
        return jsonify({"error": "El campo nombre es requerido"}), 400

    try:
        equipo = db_buscar_equipo_por_id(id)
        if not equipo:
            return jsonify({"error": "Equipo no encontrado"}), 404
        db_editar_equipo(id, nombre, descripcion)
    except Exception as e:
        return jsonify({"error": f"Error al editar equipo: {str(e)}"}), 500
    return jsonify({"message": "Equipo actualizado correctamente"}), 200


@equipos_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_equipo(id):
    try:
        equipo = db_buscar_equipo_por_id(id)
        if not equipo:
            return jsonify({"error": "Equipo no encontrado"}), 404
        db_eliminar_equipo(id)
    except Exception as e:
        return jsonify({"error": f"Error al eliminar equipo: {str(e)}"}), 500
    return "", 204


@equipos_bp.route("/<int:id>/alumnos", methods=["POST"])
def asociar_alumnos(id):
    data = request.get_json()
    alumnos_ids = data.get("alumnos")

    if not alumnos_ids or not isinstance(alumnos_ids, list):
        return jsonify({"error": "Se requiere una lista de IDs bajo la clave 'alumnos'"}), 400

    try:
        equipo = db_buscar_equipo_por_id(id)
        if not equipo:
            return jsonify({"error": "Equipo no encontrado"}), 404
        db_asociar_alumnos(id, alumnos_ids)
    except Exception as e:
        return jsonify({"error": f"Error al asociar alumnos: {str(e)}"}), 500
    return jsonify({"message": "Alumnos asociados al equipo correctamente"}), 200


@equipos_bp.route("/<int:id>/alumnos/<int:alumno_id>", methods=["DELETE"])
def quitar_alumno(id, alumno_id):
    try:
        equipo = db_buscar_equipo_por_id(id)
        if not equipo:
            return jsonify({"error": "Equipo no encontrado"}), 404
        db_quitar_alumno_equipo(id, alumno_id)
    except Exception as e:
        return jsonify({"error": f"Error al quitar alumno: {str(e)}"}), 500
    return jsonify({"message": "Alumno quitado del equipo"}), 200


@equipos_bp.route("/<int:id>/tps", methods=["POST"])
def asociar_equipos_a_tp(id):
    data = request.get_json()
    evaluacion_id = data.get("evaluacion_id")

    if not evaluacion_id:
        return jsonify({"error": "El campo evaluacion_id es requerido"}), 400

    try:
        integrantes = db_listar_alumnos_equipo(id)
        if not integrantes:
            return jsonify({"error": "El equipo no tiene alumnos asociados todavía. Asocie alumnos primero."}), 400
        db_asociar_equipo_a_tp(id, evaluacion_id, integrantes)
    except Exception as e:
        return jsonify({"error": f"Error al asociar equipo al TP: {str(e)}"}), 500
    return jsonify({"message": "Equipo asociado al Trabajo Práctico con éxito"}), 200
