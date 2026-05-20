from backend.db import get_db_connection

def db_obtener_todas_las_evaluaciones():
    conexion = get_db_connection()
    if conexion is None:
        return []
    
    cursor = conexion.cursor(dictionary=True) 
    try:
        cursor.execute("SELECT id_evaluacion, nombre, tipo, fecha, estado FROM Evaluacion")
        resultados = cursor.fetchall()
        return resultados
    except Exception as e:
        print(f"Error al obtener evaluaciones de la BD: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()