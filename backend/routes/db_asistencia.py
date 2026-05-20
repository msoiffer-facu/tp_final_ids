import json
import mysql.connector


def get_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="root", database="tp"
    )


def obtener_clases_p():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clase_presencial")
    clases_p = cursor.fetchall()
    cursor.close()
    return clases_p

def crear_clase_p(fecha, curso):
    db = get_db()
    print(curso['id'])
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO clase_presencial (curso_id, fecha) VALUES (%s, %s)",
        (curso['id'], fecha)
    )
    db.commit()
    cursor.close()

def buscar_clase_p(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clase_presencial WHERE id = %s",(id,))
    curso = cursor.fetchone()
    cursor.close()
    return curso

def actualizar_clase_p(id, fecha, curso_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE clase_presencial SET fecha = %s, curso_id = %s WHERE id = %s",
        (fecha, curso_id, id),
    )
    db.commit()
    cursor.close()

def eliminar_clase_p(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM clase_presencial WHERE id = %s", (id,))
    db.commit()
    cursor.close()

def crear_asistencia_alumnos(alumnos, clase_id):
    db = get_db()
    cursor = db.cursor()

    datos = [(alumno['id'], clase_id) for alumno in alumnos]

    query = "INSERT INTO asistencias (alumno_id, clase_presencial_id) VALUES (%s, %s)"
    cursor.executemany(query, datos)
    db.commit()
    cursor.close()

#TODO: cambiar la siguiente funcion a un archivo de curso y no dejarlo en el repository de asistencia

def buscar_curso(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos WHERE id = %s",(id,))
    curso = cursor.fetchone()
    cursor.close()
    return curso

def obtener_cursos():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos")
    cursos = cursor.fetchall()
    cursor.close()
    return cursos

def listar_alumnos_por_curso(curso_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alumnos WHERE curso_id = %s", (curso_id,))
    curso = cursor.fetchall()
    cursor.close()
    return curso