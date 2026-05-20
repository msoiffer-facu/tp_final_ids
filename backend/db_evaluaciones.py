from backend.db import get_db_connection

def db_obtener_todas_las_evaluaciones():
    conexion = get_db_connection()
    if conexion is None:
        return []
    
    cursor = conexion.cursor(dictionary=True)
    try:
        query = "SELECT id_evaluacion, nombre, tipo, fecha, estado FROM Evaluacion"
        cursor.execute(query)
        resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al obtener evaluaciones de la BD: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()

def db_obtener_notas_evaluacion(id_evaluacion):
    conexion = get_db_connection()
    if conexion is None:
        return []
    
    cursor = conexion.cursor(dictionary=True)
    try:
        query = """
            SELECT a.legajo, a.nombre, n.nota 
            FROM Alumno a
            LEFT JOIN Nota n ON a.id_alumno = n.id_alumno AND n.id_evaluacion = %s
        """
        cursor.execute(query, (id_evaluacion,))
        resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al obtener notas de la BD para la evaluación {id_evaluacion}: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()