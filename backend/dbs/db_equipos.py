from db import get_db

def db_listar_equipos_alumno(alumno_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT equipos.id, equipos.nombre, equipos.descripcion, equipos.curso_id, equipos.fecha_creacion FROM equipos
            JOIN equipo_alumnos ON equipos.id = equipo_alumnos.equipo_id
            WHERE equipo_alumnos.alumno_id = %s""", (alumno_id,))
       
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def db_listar_equipos():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre, descripcion, curso_id, fecha_creacion FROM equipos")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def db_crear_equipo(nombre, descripcion, curso_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO equipos (nombre, descripcion, curso_id) VALUES (%s, %s, %s)",
            (nombre, descripcion, curso_id)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def db_buscar_equipo_por_id(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre, descripcion, curso_id, fecha_creacion FROM equipos WHERE id = %s", (id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def db_editar_equipo(id, nombre, descripcion):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE equipos SET nombre = %s, descripcion = %s WHERE id = %s",
            (nombre, descripcion, id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def db_eliminar_equipo(id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM equipo_alumnos WHERE equipo_id = %s", (id,))
        cursor.execute("DELETE FROM equipos WHERE id = %s", (id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def db_asociar_alumnos(equipo_id, alumnos_ids):
    conn = get_db()
    cursor = conn.cursor()
    try:
        for alumno_id in alumnos_ids:
            cursor.execute(
                "SELECT 1 FROM equipo_alumnos WHERE equipo_id = %s AND alumno_id = %s",
                (equipo_id, alumno_id)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO equipo_alumnos (equipo_id, alumno_id) VALUES (%s, %s)",
                    (equipo_id, alumno_id)
                )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def db_listar_alumnos_equipo(equipo_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT alumno_id FROM equipo_alumnos WHERE equipo_id = %s", (equipo_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def db_asociar_equipo_a_tp(equipo_id, evaluacion_id, integrantes):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
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
    finally:
        cursor.close()
        conn.close()
