from flask import Blueprint, jsonify, request
from backend.db_evaluaciones import (
    db_obtener_todas_las_evaluaciones, db_eliminar_evaluacion_bd,
    db_obtener_tipos_evaluacion, db_eliminar_tipo_bd,
    db_obtener_notas_evaluacion
)

evaluaciones_bp = Blueprint('evaluaciones_bp', __name__)

EVALUACIONES_MEMORIA = []
TIPOS_MEMORIA = []

@evaluaciones_bp.route('/', methods=['GET'])
def obtener_evaluaciones():
    try:
        datos_bd = db_obtener_todas_las_evaluaciones()
        if datos_bd: return jsonify(datos_bd), 200
    except Exception: pass
    return jsonify(EVALUACIONES_MEMORIA), 200

@evaluaciones_bp.route('/', methods=['POST'])
def crear_evaluacion():
    data = request.get_json()
    if not data or 'nombre' not in data or 'tipo' not in data or 'fecha' not in data:
        return jsonify({"error": "Faltan datos obligatorios"}), 400
    
    nueva = {
        "id_evaluacion": len(EVALUACIONES_MEMORIA) + 1,
        "nombre": data['nombre'],
        "tipo": data['tipo'],
        "fecha": data['fecha'],
        "estado": data.get('estado', 'abierto')
    }
    EVALUACIONES_MEMORIA.append(nueva)
    return jsonify({"mensaje": "Evaluación creada con éxito", "evaluacion": nueva}), 201

@evaluaciones_bp.route('/<int:id_evaluacion>', methods=['PUT'])
def modificar_evaluacion(id_evaluacion):
    data = request.get_json()
    for ev in EVALUACIONES_MEMORIA:
        if ev['id_evaluacion'] == id_evaluacion:
            ev['nombre'] = data.get('nombre', ev['nombre'])
            ev['tipo'] = data.get('tipo', ev['tipo'])
            ev['fecha'] = data.get('fecha', ev['fecha'])
            ev['estado'] = data.get('estado', ev['estado'])
            return jsonify({"mensaje": "Evaluación modificada con éxito", "evaluacion": ev}), 200
    return jsonify({"error": "Evaluación no encontrada"}), 404

@evaluaciones_bp.route('/<int:id_evaluacion>', methods=['DELETE'])
def eliminar_evaluacion(id_evaluacion):
    eliminado = db_eliminar_evaluacion_bd(id_evaluacion)
    if eliminado:
        return jsonify({"mensaje": "Evaluación eliminada de la BD"}), 200
        
    for i, ev in enumerate(EVALUACIONES_MEMORIA):
        if ev['id_evaluacion'] == id_evaluacion:
            EVALUACIONES_MEMORIA.pop(i)
            return jsonify({"mensaje": "Evaluación eliminada de la memoria"}), 200
    return jsonify({"error": "Evaluación no encontrada"}), 404


@evaluaciones_bp.route('/tipos', methods=['GET'])
def obtener_tipos():
    try:
        datos_bd = db_obtener_tipos_evaluacion()
        if datos_bd: return jsonify(datos_bd), 200
    except Exception: pass
    return jsonify(TIPOS_MEMORIA), 200

@evaluaciones_bp.route('/tipos', methods=['POST'])
def crear_tipo():
    data = request.get_json()
    if not data or 'descripcion' not in data:
        return jsonify({"error": "Falta la descripción del tipo"}), 400
    
    nuevo_tipo = {
        "id_tipo": len(TIPOS_MEMORIA) + 1,
        "descripcion": data['descripcion']
    }
    TIPOS_MEMORIA.append(nuevo_tipo)
    return jsonify({"mensaje": "Tipo de evaluación creado", "tipo": nuevo_tipo}), 201

@evaluaciones_bp.route('/tipos/<int:id_tipo>', methods=['PUT'])
def modificar_tipo(id_tipo):
    data = request.get_json()
    for t in TIPOS_MEMORIA:
        if t['id_tipo'] == id_tipo:
            t['descripcion'] = data.get('descripcion', t['descripcion'])
            return jsonify({"mensaje": "Tipo modificado con éxito", "tipo": t}), 200
    return jsonify({"error": "Tipo de evaluación no encontrado"}), 404

@evaluaciones_bp.route('/tipos/<int:id_tipo>', methods=['DELETE'])
def eliminar_tipo(id_tipo):
    eliminado = db_eliminar_tipo_bd(id_tipo)
    if eliminado:
        return jsonify({"mensaje": "Tipo eliminado de la BD"}), 200
        
    for i, t in enumerate(TIPOS_MEMORIA):
        if t['id_tipo'] == id_tipo:
            TIPOS_MEMORIA.pop(i)
            return jsonify({"mensaje": "Tipo eliminado de la memoria"}), 200
    return jsonify({"error": "Tipo no encontrado"}), 404


@evaluaciones_bp.route('/<int:id_evaluacion>/notas-individuales', methods=['GET'])
def obtener_notas_individuales(id_evaluacion):
    try:
        notas_bd = db_obtener_notas_evaluacion(id_evaluacion)
        if notas_bd:
            return jsonify({"id_evaluacion": id_evaluacion, "alumnos_notas": notas_bd}), 200
    except Exception: pass
    return jsonify({"id_evaluacion": id_evaluacion, "alumnos_notas": []}), 200

@evaluaciones_bp.route('/validar-nota', methods=['POST'])
def validar_nota():
    data = request.get_json()
    if not data or 'nota' not in data:
        return jsonify({"error": "Falta la nota a validar"}), 400
    
    try:
        nota = float(data['nota'])
    except ValueError:
        return jsonify({"valida": False, "error": "La nota debe ser un número"}), 400

    if 1.0 <= nota <= 10.0:
        return jsonify({"valida": True, "mensaje": "Nota en rango válido"}), 200
    else:
        return jsonify({"valida": False, "error": "La nota debe estar entre 1 y 10"}), 422