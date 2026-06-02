from db import get_db

def db_get_alumnos(offset, limit=10, busqueda="", abandono=""):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    texto = f"%{busqueda}%"
    params = []
    where_clauses = []

    if busqueda != "":
        where_clauses.append("(nombre LIKE %s OR apellido LIKE %s OR CAST(padron AS CHAR) LIKE %s OR email LIKE %s)")
        params.extend([texto, texto, texto, texto])

    if abandono != "":
        where_clauses.append("abandono = %s")
        params.append(abandono)

    where_clause = ""
    if where_clauses:
        where_clause = " WHERE " + " AND ".join(where_clauses)

    query = (
        "SELECT a.id, a.padron, a.nombre, a.apellido, a.email, a.abandono, a.estado, "
        "IF((SELECT COUNT(*) FROM equipo_alumnos ea WHERE ea.alumno_id = a.id) > 0, 1, 0) AS equipo "
        "FROM alumnos a "
        f"{where_clause} "
        "LIMIT %s OFFSET %s"
    )
    cursor.execute(query, tuple(params + [limit, offset]))
    alumnos = cursor.fetchall()

    count_query = f"SELECT COUNT(*) as total FROM alumnos a{where_clause}"
    cursor.execute(count_query, tuple(params))
    total = cursor.fetchone()["total"]

    cursor.close()
    db.close()
    return alumnos, total

def db_get_alumno_id(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alumnos WHERE id=%s", (id,))
    alumno = cursor.fetchone()
    cursor.close()
    db.close()
    return alumno

def db_delete_alumno(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM alumnos WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()

def db_create_alumno(nombre, apellido, email, padron, abandono, estado):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO alumnos (nombre, apellido, email, padron, abandono, estado) VALUES (%s, %s, %s, %s, %s, %s)",
        (nombre, apellido, email, padron, abandono, estado)
        )
    db.commit()
    cursor.close()
    db.close()

def db_update_alumno(id, nombre=None, apellido=None, email=None, padron=None, abandono=None, estado=None):
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

        db_create_alumno(alumno["nombre"], alumno["apellido"], alumno["email"], alumno["padron"], alumno["abandono"], alumno["estado"])
        insertados += 1

    return {
        "insertados": insertados,
        "existentes": existentes,
        "errores": errores
    }