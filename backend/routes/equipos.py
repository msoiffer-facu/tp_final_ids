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
        # Verificar si existe el equipo primero
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