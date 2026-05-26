from db import get_db

def db_obtener_todas_las_evaluaciones():
    conexion = get_db()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, titulo, fecha, tipo_id, curso_id FROM evaluaciones")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener evaluaciones: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()

def db_eliminar_evaluacion_bd(id_evaluacion):
    conexion = get_db()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM evaluaciones WHERE id = %s", (id_evaluacion,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al eliminar evaluación: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()

def db_obtener_tipos_evaluacion():
    conexion = get_db()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre FROM tipos_evaluacion")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener tipos de evaluación: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()

def db_eliminar_tipo_bd(id_tipo):
    conexion = get_db()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM tipos_evaluacion WHERE id = %s", (id_tipo,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al eliminar tipo de evaluación: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()

def db_obtener_notas_evaluacion(id_evaluacion):
    conexion = get_db()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        query = """
            SELECT a.padron, a.nombre, a.apellido, n.nota_alumno
            FROM alumnos a
            LEFT JOIN notas n ON a.id = n.alumno_id AND n.evaluacion_id = %s
        """
        cursor.execute(query, (id_evaluacion,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener notas: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()
