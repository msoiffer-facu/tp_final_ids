from flask import Blueprint, request, jsonify
from backend.db import get_db_connection
from backend.swagger.db_notas import crear_nota_db, obtener_notas_db, notas_alumno_db, notas_equipo_db, modificar_nota_db, eliminar_nota_db


notas_bp = Blueprint("notas", __name__)

@notas_bp.route("/notas", methods=["POST"])
def crear_nota():
    data = request.get_json()

    alumno_id = data.get("alumno_id")
    evaluacion_id = data.get("evaluacion_id")
    nota_alumno = data.get("nota_alumno")


    if alumno_id is None or evaluacion_id is None:
       return jsonify({"error": "alumno_id y evaluacion_id son obligatorios"}), 400
    

    nueva_nota_id = crear_nota_db(alumno_id, evaluacion_id, nota_alumno)


    return jsonify({"mensaje": "Nota creada correctamente","id": nueva_nota_id}), 201


@notas_bp.route("/notas", methods=["GET"])
def obtener_notas():
    try:
        notas = obtener_notas_db()
        return jsonify(notas), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notas_bp.route("/notas/alumno/<int:alumno_id>", methods=["GET"])
def alumno_notas(alumno_id):
   try:
       notas_alumno = notas_alumno_db(alumno_id)
       return jsonify(notas_alumno), 200
   
   except Exception as e:
        return jsonify({"error": str(e)}), 500


@notas_bp.route("/notas/equipo/<int:equipo_id>", methods=["GET"])
def equipo_notas(equipo_id):
    try:
       notas_equipo = notas_equipo_db(equipo_id)
       return jsonify(notas_equipo), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

@notas_bp.route("/notas/<int:nota_id>", methods=["PUT"])
def modificar_nota(nota_id):
    data = request.get_json()
    nota_alumno = data.get("nota_alumno")

    if nota_alumno is None:
        return jsonify({"error": "nota_alumno es obligatoria"}), 400

    try:
        nota_alumno = float(nota_alumno)

    except (TypeError, ValueError):
        return jsonify({"error": "nota_alumno debe ser numérica"}), 400
    
    if nota_alumno < 0 or nota_alumno > 10:
        return jsonify({"error": "La nota debe estar entre 0 y 10"}), 400

    try:
        modificar = modificar_nota_db(nota_id, nota_alumno)

        if modificar == 0:
            return jsonify({"error": "Nota no encontrada"}), 404

        return jsonify({"mensaje": "Nota modificada correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@notas_bp.route("/notas/<int:nota_id>", methods=["DELETE"])
def eliminar_nota(nota_id):

    try:
        eliminar = eliminar_nota_db(nota_id)

        if eliminar == 0:

            return jsonify({"error": "Nota no encontrada"}), 404
        return jsonify({"mensaje": "Nota eliminada correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500