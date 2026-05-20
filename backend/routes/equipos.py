from flask import Blueprint, jsonify, request
from backend.db import get_db_connection

equipos_bp = Blueprint("equipos", __name__)

@equipos_bp.route("/", methods=["GET"])
def listar_equipos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT id, nombre, descripcion, curso_id, fecha_creacion FROM equipos")
        equipos = cursor.fetchall()
        return jsonify(equipos), 200
    except Exception as e:
        return jsonify({"error": f"Error al listar equipos: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@equipos_bp.route("/", methods=["POST"])
def crear_equipo():
    data = request.get_json()
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    curso_id = data.get("curso_id")
    
    if not nombre or not curso_id:
        return jsonify({"error": "Faltan campos obligatorios: nombre y curso_id"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO equipos (nombre, descripcion, curso_id) VALUES (%s, %s, %s)",
            (nombre, descripcion, curso_id)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        return jsonify({"message": "Equipo creado con éxito", "id": nuevo_id}), 201
    except Exception as e:
        return jsonify({"error": f"Error al crear el equipo: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@equipos_bp.route("/<int:id>", methods=["PUT"])
def editar_equipo(id):
    data = request.get_json()
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    
    if not nombre:
        return jsonify({"error": "El campo nombre es requerido"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM equipos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Equipo no encontrado"}), 404
            
        cursor.execute(
            "UPDATE equipos SET nombre = %s, descripcion = %s WHERE id = %s",
            (nombre, descripcion, id)
        )
        conn.commit()
        return jsonify({"message": "Equipo actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al editar equipo: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@equipos_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_equipo(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM equipos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Equipo no encontrado"}), 404
            
        cursor.execute("DELETE FROM equipo_alumnos WHERE equipo_id = %s", (id,))
        cursor.execute("DELETE FROM equipos WHERE id = %s", (id,))
        conn.commit()
        
        return "", 204
    except Exception as e:
        return jsonify({"error": f"Error al eliminar equipo: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@equipos_bp.route("/<int:id>/alumnos", methods=["POST"])
def asociar_alumnos(id):
    data = request.get_json()
    alumnos_ids = data.get("alumnos") 
    
    if not alumnos_ids or not isinstance(alumnos_ids, list):
        return jsonify({"error": "Se requiere una lista de IDs bajo la clave 'alumnos'"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for alumno_id in alumnos_ids:            
            cursor.execute(
                "SELECT 1 FROM equipo_alumnos WHERE equipo_id = %s AND alumno_id = %s",
                (id, alumno_id)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO equipo_alumnos (equipo_id, alumno_id) VALUES (%s, %s)",
                    (id, alumno_id)
                )
        conn.commit()
        return jsonify({"message": "Alumnos asociados al equipo correctamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al asociar alumnos: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@equipos_bp.route("/<int:id>/tps", methods=["POST"])
def asociar_equipos_a_tp(id):
    data = request.get_json()
    evaluacion_id = data.get("evaluacion_id")  
    
    if not evaluacion_id:
        return jsonify({"error": "El campo evaluacion_id es requerido"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT alumno_id FROM equipo_alumnos WHERE equipo_id = %s", (id,))
        integrantes = cursor.fetchall()
        
        if not integrantes:
            return jsonify({"error": "El equipo no tiene alumnos asociados todavía. Asocie alumnos primero."}), 400
            
        for integrante in integrantes:
            alumno_id = integrante["alumno_id"]
            
            cursor.execute(
                "SELECT id FROM notas WHERE alumno_id = %s AND evaluacion_id = %s", 
                (alumno_id, evaluacion_id)
            )
            
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO notas (alumno_id, evaluacion_id, nota_alumno) VALUES (%s, %s, %s)",
                    (alumno_id, evaluacion_id, 0)
                )
                
        conn.commit()
        return jsonify({"message": "Equipo asociado al Trabajo Práctico con éxito (Alumnos asignados en tabla notas)"}), 200
    except Exception as e:
        return jsonify({"error": f"Error al asociar equipo al TP: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()