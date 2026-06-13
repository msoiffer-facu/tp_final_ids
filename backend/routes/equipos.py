from flask import Blueprint, jsonify, request, session
from dbs.db_equipos import (
    db_listar_equipos_alumno,
    db_listar_equipos,
    db_crear_equipo,
    db_buscar_equipo_por_id,
    db_editar_equipo,
    db_eliminar_equipo,
    db_asociar_alumnos,
    db_quitar_alumno_equipo,
    db_listar_alumnos_equipo,
    db_asociar_equipo_a_tp,
    db_listar_evaluaciones_equipo,
    db_desasociar_evaluacion_equipo,
    db_verificar_evaluacion_equipo,
)
from dbs.db_historial import registrar_historial_equipos

equipos_bp = Blueprint("equipos", __name__)

@equipos_bp.route("/alumno/<int:alumno_id>", methods=["GET"])
def equipos_por_alumno(alumno_id):
    try:
        equipos = db_listar_equipos_alumno(alumno_id)
        return jsonify(equipos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

        registrar_historial_equipos(f"Creó el equipo '{nombre}'", session.get("email"))

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

        registrar_historial_equipos(f"Creó el equipo '{nombre}'", session.get("email"))
        
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

        registrar_historial_equipos(f"Eliminó el equipo '{equipo['nombre']}'", session.get("email"))

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

        registrar_historial_equipos(f"Asoció alumnos al equipo '{equipo['nombre']}'", session.get("email"))

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

        registrar_historial_equipos(f"Quitó un alumno del equipo '{equipo['nombre']}'", session.get("email"))

    except Exception as e:
        return jsonify({"error": f"Error al quitar alumno: {str(e)}"}), 500
    return jsonify({"message": "Alumno quitado del equipo"}), 200


@equipos_bp.route("/<int:id>/evaluaciones", methods=["GET"])
def listar_evaluaciones_equipo(id):
    try:
        evaluaciones = db_listar_evaluaciones_equipo(id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(evaluaciones), 200


@equipos_bp.route("/<int:id>/tps", methods=["POST"])
def asociar_equipos_a_tp(id):
    data = request.get_json()
    evaluacion_id = data.get("evaluacion_id")

    if not evaluacion_id:
        return jsonify({"error": "El campo evaluacion_id es requerido"}), 400

    try:
        equipo = db_buscar_equipo_por_id(id)
        if not equipo:
            return jsonify({"error": "Equipo no encontrado"}), 404
        
        integrantes = db_listar_alumnos_equipo(id)
        if not integrantes:
            return jsonify({"error": "El equipo no tiene alumnos asociados todavía. Asocie alumnos primero."}), 400
        
        db_asociar_equipo_a_tp(id, evaluacion_id, integrantes)

        registrar_historial_equipos(f"Asoció el equipo '{equipo['nombre']}' a una evaluación", session.get("email"))

    except Exception as e:
        error_msg = str(e)
        if "ya está asociado" in error_msg:
            return jsonify({"error": error_msg}), 409
        return jsonify({"error": f"Error al asociar equipo al TP: {error_msg}"}), 500
    return jsonify({"message": "Equipo asociado al Trabajo Práctico con éxito"}), 200


@equipos_bp.route("/<int:id>/tps/<int:evaluacion_id>", methods=["DELETE"])
def desasociar_equipos_a_tp(id, evaluacion_id):
    try:
        equipo = db_buscar_equipo_por_id(id)
        if not equipo:
            return jsonify({"error": "Equipo no encontrado"}), 404
        
        if not db_verificar_evaluacion_equipo(id, evaluacion_id):
            return jsonify({"error": "Este equipo no está asociado a esta evaluación"}), 404
        
        db_desasociar_evaluacion_equipo(id, evaluacion_id)
 
        registrar_historial_equipos(f"Desasoció el equipo '{equipo['nombre']}' de una evaluación", session.get("email"))

    except Exception as e:
        return jsonify({"error": f"Error al desasociar equipo del TP: {str(e)}"}), 500
    return jsonify({"message": "Equipo desasociado del Trabajo Práctico con éxito"}), 200
