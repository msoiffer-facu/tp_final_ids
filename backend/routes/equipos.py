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


