from db import get_db

def obtener_alumnos_exportar():
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT nombre,
               apellido,
               email,
               padron,
               abandono
        FROM alumnos
    """)

    alumnos = cursor.fetchall()

    cursor.close()
    db.close()

    return alumnos