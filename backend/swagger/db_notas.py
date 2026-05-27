from flask import jsonify
from backend.db import get_db_connection


def crear_nota_db(alumno_id, evaluacion_id, nota_alumno):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""INSERT INTO notas (alumno_id, evaluacion_id, nota_alumno) VALUES (%s, %s, %s)""", (alumno_id, evaluacion_id, nota_alumno))
        conn.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        conn.close()

def obtener_notas_db():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT notas.id, notas.nota_alumno, alumnos.nombre, alumnos.apellido, evaluaciones.titulo, evaluaciones.fecha, tipos_evaluacion.nombre
            FROM notas
            JOIN alumnos
                ON notas.alumno_id = alumnos.id

            JOIN evaluaciones
                ON notas.evaluacion_id = evaluaciones.id
                    
            JOIN tipos_evaluacion
                ON evaluaciones.tipo_id = tipos_evaluacion.id""")
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def notas_alumno_db(alumno_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT notas.id, notas.nota_alumno, alumnos.nombre, alumnos.apellido, evaluaciones.titulo, evaluaciones.fecha, tipos_evaluacion.nombre
            FROM notas
            JOIN alumnos
                ON notas.alumno_id = alumnos.id

            JOIN evaluaciones
                ON notas.evaluacion_id = evaluaciones.id

            JOIN tipos_evaluacion
                ON evaluaciones.tipo_id = tipos_evaluacion.id

            WHERE notas.alumno_id = %s""", (alumno_id,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def notas_equipo_db(equipo_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT notas.id, notas.nota_alumno, alumnos.padron, alumnos.nombre, alumnos.apellido, evaluaciones.titulo, evaluaciones.fecha, tipos_evaluacion.nombre AS tipo_evaluacion, equipos.nombre
            FROM notas
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
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def modificar_nota_db(nota_id, nota_alumno):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""UPDATE notas SET nota_alumno = %s WHERE id = %s""", (nota_alumno, nota_id))
        conn.commit()
        return cursor.rowcount

    finally:
        cursor.close()
        conn.close()


def eliminar_nota_db(nota_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""DELETE FROM notas WHERE id = %s""", (nota_id,))
        conn.commit()
        return cursor.rowcount

    finally:
        cursor.close()
        conn.close()