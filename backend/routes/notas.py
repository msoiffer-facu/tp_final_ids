from flask import Blueprint, jsonify, request

from dbs.db_notas import crear_nota_db, obtener_notas_db, obtener_notas_alumno_db, obtener_notas_equipo_db, modificar_nota_db, eliminar_nota_db

notas_bp = Blueprint("notas", __name__)

@notas_bp.route("/", methods=["POST"])
def crear_nota():
 
 data = request.get_json()

 alumno_id = data.get("alumno_id")
 evaluacion_id = data.get("evaluacion_id")
 nota_alumno = data.get("nota_alumno")
 estado = data.get("estado")
 try:
    nueva_nota_id = crear_nota_db(alumno_id, evaluacion_id, nota_alumno, estado)

 except Exception as e:
    return jsonify({"error": str(e)}), 500
 
 return jsonify({"mensaje": "Nota creada correctamente", "nota_id": nueva_nota_id}), 201


@notas_bp.route("/", methods=["GET"])
def obtener_notas():
 try:
    notas = obtener_notas_db()

 except Exception as e:
    return jsonify({"error": str(e)}), 500

 return jsonify(notas), 200


@notas_bp.route("/alumno/<int:alumno_id>", methods=["GET"])
def alumno_notas(alumno_id):
 try:
    notas_alumno = obtener_notas_alumno_db(alumno_id)

 except Exception as e:
    return jsonify({"error": str(e)}), 500

 return jsonify(notas_alumno), 200

@notas_bp.route("/equipo/<int:equipo_id>", methods=["GET"])
def equipo_notas(equipo_id):
 try:
    notas_equipo = obtener_notas_equipo_db(equipo_id)

 except Exception as e:
    return jsonify({"error": str(e)}), 500

 return jsonify(notas_equipo), 200

@notas_bp.route("/<int:nota_id>", methods=["PUT"])
def modificar_nota(nota_id):
    data = request.get_json()
    nota_alumno = data.get("nota_alumno")
    
    if nota_alumno is None:
        return jsonify({"error": "El campo nota_alumno es requerido"}), 400
    
    if nota_alumno >= 7:
        estado = "PROMOCIONADO"
    
    elif nota_alumno >= 4:
        estado = "APROBADO"

    else:
        estado = "DESAPROBADO"

    try:
        filas_afectadas = modificar_nota_db(nota_id, nota_alumno, estado)

        if filas_afectadas == 0:
            return jsonify({"error": "Nota no encontrada"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    return jsonify({"mensaje": "Nota modificada correctamente"}), 200

@notas_bp.route("/<int:nota_id>", methods=["DELETE"])
def eliminar_nota(nota_id):
 try:
    filas_afectadas = eliminar_nota_db(nota_id)

    if filas_afectadas == 0:
        return jsonify({"error": "Nota no encontrada"}), 404

 except Exception as e:
    return jsonify({"error": str(e)}), 500

 return jsonify({"mensaje": "Nota eliminada correctamente"}), 200