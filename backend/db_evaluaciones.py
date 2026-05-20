from backend.db import get_db_connection

def db_obtener_todas_las_evaluaciones():
    conexion = get_db_connection()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_evaluacion, nombre, tipo, fecha, estado FROM Evaluacion")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener evaluaciones: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()

def db_eliminar_evaluacion_bd(id_evaluacion):
    conexion = get_db_connection()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM Evaluacion WHERE id_evaluacion = %s", (id_evaluacion,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al eliminar evaluación: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()

def db_obtener_tipos_evaluacion():
    conexion = get_db_connection()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id_tipo, descripcion FROM TipoEvaluacion")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener tipos de evaluación: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()

def db_eliminar_tipo_bd(id_tipo):
    conexion = get_db_connection()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        cursor.execute("DELETE FROM TipoEvaluacion WHERE id_tipo = %s", (id_tipo,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al eliminar tipo de evaluación: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()

def db_obtener_notas_evaluacion(id_evaluacion):
    conexion = get_db_connection()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        query = """
            SELECT a.legajo, a.nombre, n.nota 
            FROM Alumno a
            LEFT JOIN Nota n ON a.id_alumno = n.id_alumno AND n.id_evaluacion = %s
        """
        cursor.execute(query, (id_evaluacion,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener notas: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()