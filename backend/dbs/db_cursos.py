
from db import get_db


# ─── CURSOS ───

def db_get_cursos(page=1, per_page=10, cuatrimestre=""):
    offset = (page - 1) * per_page
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    where = "WHERE c.cuatrimestre = %s" if cuatrimestre else ""
    params_count = (cuatrimestre,) if cuatrimestre else ()

    cursor.execute(f"SELECT COUNT(*) as total FROM cursos c {where}", params_count)
    total = cursor.fetchone()["total"]

    query = f"""
        SELECT c.*, COUNT(ac.alumnos_id) as cantidad_alumnos
        FROM cursos c
        LEFT JOIN alumnos_curso ac ON ac.curso_id = c.id
        {where}
        GROUP BY c.id
    """

    if per_page == -1:
        cursor.execute(query, params_count)
    else:
        cursor.execute(query + " LIMIT %s OFFSET %s", params_count + (per_page, offset))

    cursos = cursor.fetchall()
    cursor.close()
    conn.close()
    return cursos, total

def get_total_alumnos_curso(curso_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM alumnos_curso WHERE curso_id = %s", (curso_id,))
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total

def db_get_curso_by_id(id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos WHERE id = %s", (id,))
    curso = cursor.fetchone()
    cursor.close()
    conn.close()
    return curso

def db_create_curso(nombre, cuatrimestre, anio, modificacion):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO cursos (nombre, cuatrimestre, anio, modificacion) VALUES (%s, %s, %s, %s)",
        (nombre, cuatrimestre, anio, modificacion)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return nuevo_id

def db_update_curso(id, nombre, cuatrimestre, anio, modificacion):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cursos SET nombre = %s, cuatrimestre = %s, anio = %s, modificacion = %s WHERE id = %s",
        (nombre, cuatrimestre, anio, modificacion, id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def db_delete_curso(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cursos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()


# ─── ALUMNOS DEL CURSO ───

def db_get_alumnos_curso(curso_id, page=1, per_page=10):
    offset = (page - 1) * per_page
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as total FROM alumnos_curso WHERE curso_id = %s", (curso_id,))
    total = cursor.fetchone()["total"]
    
    cursor.execute("""
        SELECT a.id, a.padron, a.nombre, a.apellido, a.email, a.abandono, a.estado
        FROM alumnos_curso ac
        JOIN alumnos a ON ac.alumnos_id = a.id
        WHERE ac.curso_id = %s
        ORDER BY a.apellido, a.nombre
        LIMIT %s OFFSET %s
    """, (curso_id, per_page, offset))
    alumnos = cursor.fetchall()
    cursor.close()
    conn.close()
    return alumnos, total

def db_inscribir_alumno(curso_id, alumno_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO alumnos_curso (alumnos_id, curso_id) VALUES (%s, %s)",
        (alumno_id, curso_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def db_desinscribir_alumno(curso_id, alumno_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM alumnos_curso WHERE curso_id = %s AND alumnos_id = %s",
        (curso_id, alumno_id)
    )
    conn.commit()
    afectados = cursor.rowcount
    cursor.close()
    conn.close()
    return afectados


# ─── CLASES PRESENCIALES ───

def db_get_clases(curso_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clase_presencial WHERE curso_id = %s ORDER BY fecha", (curso_id,))
    clases = cursor.fetchall()
    cursor.close()
    conn.close()
    return clases

def db_create_clase(curso_id, fecha):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clase_presencial (curso_id, fecha) VALUES (%s, %s)",
        (curso_id, fecha)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return nuevo_id

def db_delete_clase(clase_id, curso_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM clase_presencial WHERE id = %s AND curso_id = %s",
        (clase_id, curso_id)
    )
    conn.commit()
    afectados = cursor.rowcount
    cursor.close()
    conn.close()
    return afectados


# ─── EQUIPOS ───

def db_get_equipos(curso_id, page=1, per_page=10):
    offset = (page - 1) * per_page
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as total FROM equipos WHERE curso_id = %s", (curso_id,))
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT * FROM equipos WHERE curso_id = %s LIMIT %s OFFSET %s", 
        (curso_id, per_page, offset))
    equipos = cursor.fetchall()
    cursor.close()
    conn.close()
    return equipos, total

def db_create_equipo(nombre, descripcion, curso_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO equipos (nombre, descripcion, curso_id) VALUES (%s, %s, %s)",
        (nombre, descripcion, curso_id)
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return nuevo_id

def db_get_alumnos_equipo(equipo_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, a.padron, a.nombre, a.apellido, a.email
        FROM equipo_alumnos ea
        JOIN alumnos a ON ea.alumno_id = a.id
        WHERE ea.equipo_id = %s
        ORDER BY a.apellido, a.nombre
    """, (equipo_id,))
    alumnos = cursor.fetchall()
    cursor.close()
    conn.close()
    return alumnos

def db_agregar_alumno_equipo(equipo_id, alumno_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO equipo_alumnos (equipo_id, alumno_id) VALUES (%s, %s)",
        (equipo_id, alumno_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

def db_quitar_alumno_equipo(equipo_id, alumno_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM equipo_alumnos WHERE equipo_id = %s AND alumno_id = %s",
        (equipo_id, alumno_id)
    )
    conn.commit()
    afectados = cursor.rowcount
    cursor.close()
    conn.close()
    return afectados
