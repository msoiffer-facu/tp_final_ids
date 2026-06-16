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
        cursor.execute("""
            SELECT e.id, e.nombre, e.descripcion, e.curso_id, e.estado, e.fecha_creacion,
                   COUNT(ea.alumno_id) AS miembros
            FROM equipos e
            LEFT JOIN equipo_alumnos ea ON ea.equipo_id = e.id
            GROUP BY e.id, e.nombre, e.descripcion, e.curso_id, e.estado, e.fecha_creacion
        """)
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
        cursor.execute("SELECT id, nombre, descripcion, curso_id, estado, fecha_creacion FROM equipos WHERE id = %s", (id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def db_editar_equipo(id, nombre, descripcion, estado):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE equipos SET nombre = %s, descripcion = %s, estado = %s WHERE id = %s",
            (nombre, descripcion, estado, id)
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


def db_quitar_alumno_equipo(equipo_id, alumno_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM equipo_alumnos WHERE equipo_id = %s AND alumno_id = %s",
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


def db_listar_evaluaciones_equipo(equipo_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT e.id, e.titulo, e.fecha
            FROM evaluaciones e
            JOIN evaluacion_equipos ee ON e.id = ee.evaluacion_id
            WHERE ee.equipo_id = %s
            ORDER BY e.fecha DESC
        """, (equipo_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def db_asociar_equipo_a_tp(equipo_id, evaluacion_id, integrantes):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # Verificar si ya existe la asociación
        cursor.execute(
            "SELECT 1 FROM evaluacion_equipos WHERE equipo_id = %s AND evaluacion_id = %s",
            (equipo_id, evaluacion_id)
        )
        if cursor.fetchone():
            raise Exception("Este equipo ya está asociado a esta evaluación")
        
        # Insertar en evaluacion_equipos
        cursor.execute(
            "INSERT INTO evaluacion_equipos (equipo_id, evaluacion_id) VALUES (%s, %s)",
            (equipo_id, evaluacion_id)
        )
        
        # Insertar notas para cada integrante
        for integrante in integrantes:
            alumno_id = integrante["alumno_id"]
            cursor.execute(
                "SELECT id FROM notas WHERE alumno_id = %s AND evaluacion_id = %s",
                (alumno_id, evaluacion_id)
            )
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO notas (alumno_id, evaluacion_id) VALUES (%s, %s)",
                    (alumno_id, evaluacion_id)
                )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def db_desasociar_evaluacion_equipo(equipo_id, evaluacion_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM evaluacion_equipos WHERE equipo_id = %s AND evaluacion_id = %s",
            (equipo_id, evaluacion_id)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def db_verificar_evaluacion_equipo(equipo_id, evaluacion_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT 1 FROM evaluacion_equipos WHERE equipo_id = %s AND evaluacion_id = %s",
            (equipo_id, evaluacion_id)
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()
