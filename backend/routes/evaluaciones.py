from flask import Blueprint, jsonify, request
from backend.db_evaluaciones import db_obtener_todas_las_evaluaciones

evaluaciones_bp = Blueprint('evaluaciones_bp', __name__)

EVALUACIONES_MOCK = [
    {"id_evaluacion": 1, "nombre": "Parcial 1", "tipo": "Parcial", "fecha": "2026-05-20", "estado": "abierto"},
    {"id_evaluacion": 2, "nombre": "TP Final", "tipo": "Trabajo Practico", "fecha": "2026-06-17", "estado": "abierto"},
    {"id_evaluacion": 3, "nombre": "Parcialito SQL", "tipo": "Parcialito", "fecha": "2026-05-27", "estado": "cerrado"}
]

@evaluaciones_bp.route('/', methods=['GET'])
def obtener_evaluaciones():
    datos_bd = db_obtener_todas_las_evaluaciones()
    
    if datos_bd:
        return jsonify(datos_bd), 200
    
    return jsonify(EVALUACIONES_MOCK), 200

@evaluaciones_bp.route('/<int:id_evaluacion>/notas-individuales', methods=['GET'])
def obtener_notas_individuales(id_evaluacion):
    NOTAS_MOCK = [
        {"id_alumno": 1, "legajo": "115305", "nombre": "Agustin Bianchi", "nota": 8.0},
        {"id_alumno": 2, "legajo": "115287", "nombre": "Santiago Luka Picone", "nota": 9.5},
        {"id_alumno": 3, "legajo": "115301", "nombre": "Alejo Hillar", "nota": None}
    ]
    return jsonify({
        "id_evaluacion": id_evaluacion,
        "alumnos_notas": NOTAS_MOCK
    }), 200