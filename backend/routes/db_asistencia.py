import json
import mysql.connector


def get_db():
    return mysql.connector.connect(
        host="localhost", user="root", password="root", database="tp"
    )


def crear_asistencia_alumnos(alumnos, id_clase):
    db = get_db()
    cursor = db.cursor()
    cursor.execute()
    db.commit()
    cursor.close()