from flask import Blueprint, request, jsonify
from backend.db import get_db_connection

notas_bp = Blueprint("notas", __name__)

@notas_bp.route("/notas", methods=["POST"])
def crear_nota():

    data = request.get_json()

    alumno_id = data.get("alumno_id")
    evaluacion_id = data.get("evaluacion_id")
    nota_alumno = data.get("nota_alumno")

    conn = get_db_connection()
    cursor = conn.cursor()

    if alumno_id is None or evaluacion_id is None:
       return jsonify({"error": "alumno_id y evaluacion_id son obligatorios"}), 400
    
    try:
        cursor.execute("""
            INSERT INTO notas (alumno_id, evaluacion_id, nota_alumno) 
            VALUES (%s, %s, %s)""", (alumno_id, evaluacion_id, nota_alumno))

        conn.commit()

        nueva_nota_id = cursor.lastrowid

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

    return jsonify({"mensaje": "Nota creada correctamente","id": nueva_nota_id}), 201


@notas_bp.route("/notas", methods=["GET"])
def obtener_notas():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
     cursor.execute("""SELECT notas.id, notas.nota_alumno, alumnos.nombre, alumnos.apellido, evaluaciones.titulo, evaluaciones.fecha, tipos_evaluacion.nombre FROM notas
            JOIN alumnos
                ON notas.alumno_id = alumnos.id
            JOIN evaluaciones
                ON notas.evaluacion_id = evaluaciones.id
        JOIN tipos_evaluacion
            ON evaluaciones.tipo_id = tipos_evaluacion.id """)
        
     notas = cursor.fetchall()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

    return jsonify(notas), 200


@notas_bp.route("/notas/alumno/<int:alumno_id>", methods=["GET"])
def alumno_notas(alumno_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT notas.id, notas.nota_alumno, alumnos.nombre, alumnos.apellido, evaluaciones.titulo, evaluaciones.fecha, tipos_evaluacion.nombre FROM notas
     JOIN alumnos
        ON notas.alumno_id = alumnos.id
     JOIN evaluaciones
        ON notas.evaluacion_id = evaluaciones.id
     JOIN tipos_evaluacion
        ON evaluaciones.tipo_id = tipos_evaluacion.id
                
     WHERE notas.alumno_id = %s""", (alumno_id,))

        notas_alumno = cursor.fetchall()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

    return jsonify(notas_alumno), 200

@notas_bp.route("/notas/equipo/<int:equipo_id>", methods=["GET"])
def equipo_notas(equipo_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:

     cursor.execute("""SELECT notas.id, notas.nota_alumno, alumnos.padron, alumnos.nombre, alumnos.apellido, evaluaciones.titulo, evaluaciones.fecha, tipos_evaluacion.nombre AS tipo_evaluacion, equipos.nombre FROM notas
        JOIN alumnos
            ON notas.alumno_id = alumnos.id
        JOIN equipo_alumnos
            ON alumnos.id = equipo_alumnos.alumno_id
        JOIN equipos
            ON equipo_alumnos.equipo_id = equipos.id
        JOIN evaluaciones
            ON notas.evaluacion_id = evaluaciones.id
        JOIN tipos_evaluacion
            ON evaluaciones.tipo_id = tipos_evaluacion.id

        WHERE equipos.id = %s""", (equipo_id,))

     notas_equipo = cursor.fetchall()
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
     cursor.close()
     conn.close()

    return jsonify(notas_equipo), 200


@notas_bp.route("/notas/<int:nota_id>", methods=["PUT"])
def modificar_nota(nota_id):
    data = request.get_json()
    nota_alumno = data.get("nota_alumno")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
     cursor.execute("""UPDATE notas SET nota_alumno = %s WHERE id = %s""", (nota_alumno, nota_id))
     conn.commit()

     if cursor.rowcount == 0:
        return jsonify({"error": "Nota no encontrada"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

    return jsonify({"mensaje": "Nota modificada correctamente"}), 200

@notas_bp.route("/notas/<int:nota_id>", methods=["DELETE"])
def eliminar_nota(nota_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
     cursor.execute("""DELETE FROM notas WHERE id = %s""", (nota_id,))
     conn.commit()

     if cursor.rowcount == 0:
         cursor.close()
         conn.close()
         return jsonify({"error": "Nota no encontrada"}), 404
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
     cursor.close()
     conn.close()

    return jsonify({"mensaje": "Nota eliminada correctamente"}), 200