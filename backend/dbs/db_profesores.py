from db import get_db


def db_get_profesores(page=1, per_page=10):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    # obtener total
    cursor.execute("SELECT COUNT(*) as total FROM profesores")
    total = cursor.fetchone().get("total", 0)

    offset = (page - 1) * per_page
    cursor.execute("SELECT * FROM profesores LIMIT %s OFFSET %s", (per_page, offset))
    profesores = cursor.fetchall()
    cursor.close()
    db.close()
    return profesores, total


def db_get_profesor_by_id(profesor_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM profesores WHERE id = %s", (profesor_id,))
    profesor = cursor.fetchone()
    cursor.close()
    db.close()
    return profesor


def db_get_profesor_by_email(email):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM profesores WHERE email = %s", (email,))
    profesor = cursor.fetchone()
    cursor.close()
    db.close()
    return profesor


def db_create_profesor(nombre, apellido, email, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO profesores (nombre, apellido, email, password) VALUES (%s, %s, %s, %s)",
        (nombre, apellido, email, password)
    )
    db.commit()
    profesor_id = cursor.lastrowid
    cursor.close()
    db.close()
    return profesor_id


def db_update_profesor(profesor_id, nombre=None, apellido=None, email=None, password=None):
    db = get_db()
    cursor = db.cursor()

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
    if password is not None:
        campos.append("password = %s")
        valores.append(password)

    if not campos:
        cursor.close()
        db.close()
        return 0

    valores.append(profesor_id)
    query = f"UPDATE profesores SET {', '.join(campos)} WHERE id = %s"
    cursor.execute(query, valores)
    db.commit()
    afectados = cursor.rowcount
    cursor.close()
    db.close()
    return afectados


def db_delete_profesor(profesor_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM profesores WHERE id = %s", (profesor_id,))
    db.commit()
    afectados = cursor.rowcount
    cursor.close()
    db.close()
    return afectados
