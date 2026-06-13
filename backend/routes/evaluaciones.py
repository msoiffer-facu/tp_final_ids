from flask import Blueprint, request, jsonify
from dbs.db_evaluaciones import (
    db_obtener_todas_las_evaluaciones,
    db_obtener_evaluacion,
    db_crear_evaluacion,
    db_actualizar_evaluacion,
    db_eliminar_evaluacion_bd,
    db_obtener_tipos_evaluacion,
    db_obtener_tipo_evaluacion,
    db_crear_tipo_evaluacion,
    db_actualizar_tipo_evaluacion,
    db_eliminar_tipo_bd,
    db_obtener_notas_evaluacion,
    db_guardar_notas_evaluacion,
)

evaluaciones_bp = Blueprint('evaluaciones', __name__)


# ─── TIPOS DE EVALUACIÓN ───

@evaluaciones_bp.route('/tipos', methods=['GET'])
def obtener_tipos():
    tipos = db_obtener_tipos_evaluacion()
    return jsonify(tipos), 200


@evaluaciones_bp.route('/tipos/<int:id_tipo>', methods=['GET'])
def obtener_tipo(id_tipo):
    tipo = db_obtener_tipo_evaluacion(id_tipo)
    if not tipo:
        return jsonify({"error": "Tipo no encontrado"}), 404
    return jsonify(tipo), 200


@evaluaciones_bp.route('/tipos', methods=['POST'])
def crear_tipo():
    data = request.get_json()
    nombre = (data or {}).get('nombre', '').strip()
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    nuevo_id = db_crear_tipo_evaluacion(nombre)
    if nuevo_id is None:
        return jsonify({"error": "No se pudo crear el tipo"}), 500
    return jsonify({"id": nuevo_id, "nombre": nombre}), 201


@evaluaciones_bp.route('/tipos/<int:id_tipo>', methods=['PUT'])
def actualizar_tipo(id_tipo):
    data = request.get_json()
    nombre = (data or {}).get('nombre', '').strip()
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    if not db_obtener_tipo_evaluacion(id_tipo):
        return jsonify({"error": "Tipo no encontrado"}), 404
    exito = db_actualizar_tipo_evaluacion(id_tipo, nombre)
    if not exito:
        return jsonify({"error": "No se pudo actualizar el tipo"}), 500
    return jsonify({"mensaje": "Tipo actualizado correctamente"}), 200


@evaluaciones_bp.route('/tipos/<int:id_tipo>', methods=['DELETE'])
def eliminar_tipo(id_tipo):
    if not db_obtener_tipo_evaluacion(id_tipo):
        return jsonify({"error": "Tipo no encontrado"}), 404
    exito = db_eliminar_tipo_bd(id_tipo)
    if not exito:
        return jsonify({"error": "No se pudo eliminar el tipo"}), 500
    return jsonify({"mensaje": "Tipo eliminado correctamente"}), 200


# ─── EVALUACIONES ───

@evaluaciones_bp.route('/', methods=['GET'])
def obtener_evaluaciones():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    tipo_id = request.args.get('tipo_id', None, type=int)
    curso_id = request.args.get('curso_id', None, type=int)
    evaluaciones, total = db_obtener_todas_las_evaluaciones(page, per_page, tipo_id, curso_id)
    return jsonify({
        "evaluaciones": evaluaciones,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if total else 0,
    }), 200


@evaluaciones_bp.route('/<int:id_evaluacion>', methods=['GET'])
def obtener_evaluacion(id_evaluacion):
    evaluacion = db_obtener_evaluacion(id_evaluacion)
    if not evaluacion:
        return jsonify({"error": "Evaluación no encontrada"}), 404
    return jsonify(evaluacion), 200


@evaluaciones_bp.route('/', methods=['POST'])
def crear_evaluacion():
    data = request.get_json() or {}
    titulo = data.get('titulo', '').strip()
    fecha = data.get('fecha')
    tipo_id = data.get('tipo_id')
    curso_id = data.get('curso_id')

    if not titulo or not fecha or not tipo_id or not curso_id:
        return jsonify({"error": "titulo, fecha, tipo_id y curso_id son obligatorios"}), 400

    nuevo_id = db_crear_evaluacion(titulo, fecha, tipo_id, curso_id)
    if nuevo_id is None:
        return jsonify({"error": "No se pudo crear la evaluación"}), 500
    return jsonify({"id": nuevo_id, "mensaje": "Evaluación creada correctamente"}), 201


@evaluaciones_bp.route('/<int:id_evaluacion>', methods=['PUT'])
def actualizar_evaluacion(id_evaluacion):
    if not db_obtener_evaluacion(id_evaluacion):
        return jsonify({"error": "Evaluación no encontrada"}), 404

    data = request.get_json() or {}
    titulo = data.get('titulo', '').strip()
    fecha = data.get('fecha')
    tipo_id = data.get('tipo_id')
    curso_id = data.get('curso_id')

    if not titulo or not fecha or not tipo_id or not curso_id:
        return jsonify({"error": "titulo, fecha, tipo_id y curso_id son obligatorios"}), 400

    exito = db_actualizar_evaluacion(id_evaluacion, titulo, fecha, tipo_id, curso_id)
    if not exito:
        return jsonify({"error": "No se pudo actualizar la evaluación"}), 500
    return jsonify({"mensaje": "Evaluación actualizada correctamente"}), 200


@evaluaciones_bp.route('/<int:id_evaluacion>', methods=['DELETE'])
def eliminar_evaluacion(id_evaluacion):
    exito = db_eliminar_evaluacion_bd(id_evaluacion)
    if exito:
        return jsonify({"mensaje": "Evaluación eliminada correctamente"}), 200
    return jsonify({"error": "No se encontró la evaluación o no se pudo eliminar"}), 404


# ─── NOTAS ───

@evaluaciones_bp.route('/<int:id_evaluacion>/notas', methods=['GET'])
def obtener_notas(id_evaluacion):
    if not db_obtener_evaluacion(id_evaluacion):
        return jsonify({"error": "Evaluación no encontrada"}), 404
    notas = db_obtener_notas_evaluacion(id_evaluacion)
    return jsonify(notas), 200


@evaluaciones_bp.route('/<int:id_evaluacion>/notas', methods=['POST'])
def guardar_notas(id_evaluacion):
    if not db_obtener_evaluacion(id_evaluacion):
        return jsonify({"error": "Evaluación no encontrada"}), 404

    data = request.get_json() or {}
    notas = data.get('notas', [])
    if not isinstance(notas, list):
        return jsonify({"error": "Se esperaba una lista de notas"}), 400

    for n in notas:
        if 'alumno_id' not in n or 'nota_alumno' not in n:
            return jsonify({"error": "Cada nota requiere alumno_id y nota_alumno"}), 400
        try:
            val = float(n['nota_alumno'])
        except (ValueError, TypeError):
            return jsonify({"error": "nota_alumno debe ser un número"}), 400
        if not (1 <= val <= 10):
            return jsonify({"error": f"La nota debe estar entre 1 y 10 (alumno_id={n['alumno_id']})"}), 422

    exito = db_guardar_notas_evaluacion(id_evaluacion, notas)
    if not exito:
        return jsonify({"error": "No se pudieron guardar las notas"}), 500
    return jsonify({"mensaje": "Notas guardadas correctamente"}), 200