from db import get_db

def db_get_alumnos(offset, limit=10, busqueda="", abandono=""):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    texto = f"%{busqueda}%"
    params = []
    where_clauses = []

    if busqueda != "":
        where_clauses.append("(a.nombre LIKE %s OR a.apellido LIKE %s OR CAST(a.padron AS CHAR) LIKE %s OR a.email LIKE %s)")
        params.extend([texto, texto, texto, texto])

    if abandono != "":
        where_clauses.append("a.abandono = %s")
        params.append(abandono)

    where_clause = ""
    if where_clauses:
        where_clause = " WHERE " + " AND ".join(where_clauses)

    query = (
        "SELECT a.*, c.nombre as curso FROM alumnos a "
        "LEFT JOIN alumnos_curso ac ON ac.alumnos_id = a.id "
        "LEFT JOIN cursos c ON c.id = ac.curso_id "
        f"{where_clause} "
        "LIMIT %s OFFSET %s"
    )
    cursor.execute(query, tuple(params + [limit, offset]))
    alumnos = cursor.fetchall()

    count_query = f"SELECT COUNT(*) as total FROM alumnos a {where_clause}"
    cursor.execute(count_query, tuple(params))
    total = cursor.fetchone()["total"]

    cursor.close()
    db.close()
    return alumnos, total

def db_get_todos_alumnos():
    """Devuelve todos los alumnos con sus equipos. Sin paginación, para selectores."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, a.nombre, a.apellido, a.padron, a.email, a.abandono,
               IFNULL(GROUP_CONCAT(e.nombre ORDER BY e.nombre SEPARATOR ', '), '') AS equipo
        FROM alumnos a
        LEFT JOIN equipo_alumnos ea ON ea.alumno_id = a.id
        LEFT JOIN equipos e ON e.id = ea.equipo_id
        GROUP BY a.id
        ORDER BY a.apellido, a.nombre
    """)
    alumnos = cursor.fetchall()
    cursor.close()
    db.close()
    return alumnos


def db_get_alumno_id(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT a.*, ac.curso_id FROM alumnos a LEFT JOIN alumnos_curso ac ON ac.alumnos_id = a.id WHERE a.id=%s", (id,))
    alumno = cursor.fetchone()
    cursor.close()
    db.close()
    return alumno

def db_delete_alumno(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM asistencias WHERE alumno_id=%s", (id,))
    cursor.execute("DELETE FROM tokens_asistencia WHERE alumno_id=%s", (id,))
    cursor.execute("DELETE FROM equipo_alumnos WHERE alumno_id=%s", (id,))
    cursor.execute("DELETE FROM notas WHERE alumno_id=%s", (id,))
    cursor.execute("DELETE FROM alumnos_curso WHERE alumnos_id=%s", (id,))
    cursor.execute("DELETE FROM alumnos WHERE id=%s", (id,))

    cursor.execute("")

    db.commit()
    cursor.close()
    db.close()

def db_create_alumno(nombre, apellido, email, padron, abandono, estado, curso_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO alumnos (nombre, apellido, email, padron, abandono, estado) VALUES (%s, %s, %s, %s, %s, %s)",
        (nombre, apellido, email, padron, abandono, estado)
        )
    db.commit()
    alumno_id = cursor.lastrowid
    if curso_id:
     cursor.execute(
        "INSERT INTO alumnos_curso (alumnos_id, curso_id) VALUES (%s, %s)",
        (alumno_id,curso_id)
        )
     db.commit()

    cursor.close()
    db.close()

def db_update_alumno(id, nombre=None, apellido=None, email=None, padron=None, abandono=None, estado=None, curso_id=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    campos = []
    valores = []
    if nombre is not None:
        campos.append("nombre = %s")
        valores.append(nombre)
    if apellido is not None:
        campos.append("apellido = %s")
        valores.append(apellido)
    if email is not None:
        campos.append("email = %s")
        valores.append(email)
    if padron is not None:
        campos.append("padron = %s")
        valores.append(padron)
    if abandono is not None:
        campos.append("abandono = %s")
        valores.append(abandono)
    if estado is not None:
        campos.append("estado = %s")
        valores.append(estado)

    if campos:
        query = f"UPDATE alumnos SET {', '.join(campos)} WHERE id = %s"
        valores.append(id)
        cursor.execute(query, tuple(valores))
        db.commit()

    # Actualizar curso si se proporciona
    if curso_id is not None:
        cursor.execute("DELETE FROM alumnos_curso WHERE alumnos_id = %s", (id,))
        if curso_id and str(curso_id).isdigit():
            cursor.execute("INSERT INTO alumnos_curso (alumnos_id, curso_id) VALUES (%s, %s)", (id, int(curso_id)))
        db.commit()

    cursor.close()
    db.close()


def db_buscar_dato_alumno (condicion, dato, id=None):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if id is not None:
        cursor.execute(f"SELECT * FROM alumnos WHERE {condicion} = %s AND id != %s", (dato, id))
    else:
        cursor.execute(f"SELECT * FROM alumnos WHERE {condicion} = %s", (dato,))
    alumno = cursor.fetchone()
    cursor.close()
    db.close()
    return alumno

def comprobar_alumno_existente(email, padron, id=None):
    errores = []

    if db_buscar_dato_alumno("email", email, id):
        errores.append("Email ya registrado")

    if db_buscar_dato_alumno("padron", padron, id):
        errores.append("Padron ya registrado")

    return errores

def cargar_alumnos_db(alumnos):
    errores = []
    insertados = 0
    existentes = 0

    for alumno in alumnos:
        
        if comprobar_alumno_existente(alumno["email"], alumno["padron"]):
            existentes += 1
            continue

        db_create_alumno(alumno["nombre"], alumno["apellido"], alumno["email"], alumno["padron"], alumno["abandono"], alumno["estado"],alumno["curso"])
        insertados += 1

    return {
        "insertados": insertados,
        "existentes": existentes,
        "errores": errores
    }

