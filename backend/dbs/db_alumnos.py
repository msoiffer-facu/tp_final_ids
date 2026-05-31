from db import get_db

def db_get_alumnos():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM alumnos")
    alumnos = cursor.fetchall()
    cursor.close()
    db.close()
    return alumnos

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