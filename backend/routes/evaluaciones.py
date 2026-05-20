from flask import Blueprint, jsonify, request
from backend.db_evaluaciones import db_obtener_todas_las_evaluaciones, db_obtener_notas_evaluacion

evaluaciones_bp = Blueprint('evaluaciones_bp', __name__)

EVALUACIONES_MEMORIA = []

@evaluaciones_bp.route('/', methods=['GET'])
def obtener_evaluaciones():
    try:
        datos_bd = db_obtener_todas_las_evaluaciones()
        if datos_bd:
            return jsonify(datos_bd), 200
    except Exception as e:
        print(f"Error al consultar evaluaciones en BD: {e}")
    
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

@evaluaciones_bp.route('/<int:id_evaluacion>/notas-individuales', methods=['GET'])
def obtener_notas_individuales(id_evaluacion):
    try:
        notas_bd = db_obtener_notas_evaluacion(id_evaluacion)
        if notas_bd:
            return jsonify({
                "id_evaluacion": id_evaluacion,
                "alumnos_notas": notas_bd
            }), 200
    except Exception as e:
        print(f"Error al consultar notas reales en BD: {e}")

    return jsonify({
        "id_evaluacion": id_evaluacion,
        "alumnos_notas": []
    }), 200