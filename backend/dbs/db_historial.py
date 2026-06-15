from db import get_db


def crear_historial(usuario, accion, area):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO historial (usuario, accion, area) VALUES (%s, %s, %s)",
        (usuario, accion, area)
    )
    db.commit()
    cursor.close()
    db.close()


def obtener_historial(limit=10):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT usuario, accion, area, hora
        FROM historial
        ORDER BY hora DESC, id DESC
        LIMIT %s
        """,
        (limit,)
    )
    historial = cursor.fetchall()
    cursor.close()
    db.close()
    return historial


def registrar_historial(usuario, accion, area):
    usuario = usuario or "Sistema"
    try:
        crear_historial(usuario, accion, area)
    except Exception as e:
        print(f"error historial: {e}")


def registrar_historial_alumnos(accion, usuario=None):
    registrar_historial(usuario, accion, "Alumnos")


def registrar_historial_cursos(accion, usuario=None):
    registrar_historial(usuario, accion, "Cursos")


def registrar_historial_asistencia(accion, usuario=None):
    registrar_historial(usuario, accion, "Asistencias")


def registrar_historial_evaluaciones(accion, usuario=None):
    registrar_historial(usuario, accion, "Evaluaciones")


def registrar_historial_profesores(accion, usuario=None):
    registrar_historial(usuario, accion, "Profesores")


def registrar_historial_notas(accion, usuario=None):
    registrar_historial(usuario, accion, "Notas")


def registrar_historial_equipos(accion, usuario=None):
    registrar_historial(usuario, accion, "Equipos")



