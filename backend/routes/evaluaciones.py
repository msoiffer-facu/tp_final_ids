from flask import Blueprint, request, jsonify
from db_evaluaciones import (
    db_obtener_todas_las_evaluaciones,
    db_eliminar_evaluacion_bd,
    db_obtener_tipos_evaluacion,
    db_obtener_notas_evaluacion
)

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('/', methods=['GET'])
def obtener_evaluaciones():
    lista = db_obtener_todas_las_evaluaciones()
    return jsonify(lista), 200

@evaluaciones_bp.route('/validar-nota', methods=['POST'])
def validar_nota():
    data = request.get_json()
    
    if not data or 'nota' not in data:
        return jsonify({"mensaje": "Falta el campo 'nota'", "valida": False}), 400
        
    try:
        nota = float(data['nota'])
    except (ValueError, TypeError):
        return jsonify({"mensaje": "La nota debe ser un número válido", "valida": False}), 422

    if 1 <= nota <= 10:
        return jsonify({"mensaje": "Nota en rango válido", "valida": True}), 200
    else:
        return jsonify({"mensaje": "La nota debe estar entre 1 y 10", "valida": False}), 422

@evaluaciones_bp.route('/<int:id_evaluacion>/notas', methods=['GET'])
def obtener_notas(id_evaluacion):
    notas = db_obtener_notas_evaluacion(id_evaluacion)
    return jsonify(notas), 200

@evaluaciones_bp.route('/<int:id_evaluacion>', methods=['DELETE'])
def eliminar_evaluacion(id_evaluacion):
    exito = db_eliminar_evaluacion_bd(id_evaluacion)
    if exito:
        return jsonify({"mensaje": "Evaluación eliminada correctamente"}), 200
    else:
        return jsonify({"mensaje": "No se encontró la evaluación o no se pudo eliminar"}), 404