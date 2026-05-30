from db import get_db


def db_crear_evaluacion_bd(titulo, fecha, tipo_id, curso_id):
    conexion = get_db()
    if conexion is None: return None
    cursor = conexion.cursor()
    try:
        query = "INSERT INTO evaluaciones (titulo, fecha, tipo_id, curso_id) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (titulo, fecha, tipo_id, curso_id))
        conexion.commit()
        return cursor.lastrowid 
    except Exception as e:
        print(f"Error al crear evaluación: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()

def db_eliminar_evaluacion_bd(id_evaluacion):
    conexion = get_db()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        query = "DELETE FROM evaluaciones WHERE id = %s"
        cursor.execute(query, (id_evaluacion,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al eliminar evaluación: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()

def db_obtener_todas_las_evaluaciones():
    conexion = get_db()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        query = """
            SELECT e.id, e.titulo, e.fecha, e.curso_id, t.nombre AS tipo_nombre, e.tipo_id, e.estado
            FROM evaluaciones e
            INNER JOIN tipos_evaluacion t ON e.tipo_id = t.id
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener evaluaciones: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()

def db_modificar_evaluacion_bd(id_evaluacion, titulo=None, fecha=None, tipo_id=None, curso_id=None):
    conexion = get_db()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        campos = []
        valores = []
        if titulo is not None:
            campos.append("titulo = %s")
            valores.append(titulo)
        if fecha is not None:
            campos.append("fecha = %s")
            valores.append(fecha)
        if tipo_id is not None:
            campos.append("tipo_id = %s")
            valores.append(tipo_id)
        if curso_id is not None:
            campos.append("curso_id = %s")
            valores.append(curso_id)
            
        valores.append(id_evaluacion)
        query = f"UPDATE evaluaciones SET {', '.join(campos)} WHERE id = %s"
        cursor.execute(query, tuple(valores))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al modificar evaluación: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()


def db_obtener_tipo_de_evaluacion_bd():
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

def db_crear_tipo_de_evaluacion_bd(nombre):
    conexion = get_db()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        cursor.execute("INSERT INTO tipos_evaluacion (nombre) VALUES (%s)", (nombre,))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al crear tipo de evaluación: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()

def db_eliminar_tipo_de_evaluacion_bd(id_tipo):
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

def db_modificar_tipo_de_evaluacion_bd(id_tipo, nuevo_nombre):
    conexion = get_db()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        query = "UPDATE tipos_evaluacion SET nombre = %s WHERE id = %s"
        cursor.execute(query, (nuevo_nombre, id_tipo))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al modificar tipo de evaluación: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()


def db_obtener_todos_los_cursos_bd():
    conexion = get_db()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre FROM cursos")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener cursos: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


def db_obtener_notas_por_evaluacion_bd(id_evaluacion):
    conexion = get_db()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        query = """
            SELECT n.id, a.nombre AS nombre_alumno, a.padron, n.nota, n.estado, n.observacion
            FROM alumnos a
            JOIN notas n ON a.id = n.alumno_id
            WHERE n.evaluacion_id = %s
        """
        cursor.execute(query, (id_evaluacion,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener notas: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()

def db_obtener_evaluacion_por_id_bd(id_evaluacion):
    conexion = get_db()
    if conexion is None: return None
    cursor = conexion.cursor(dictionary=True)
    try:
        query = "SELECT * FROM evaluaciones WHERE id = %s"
        cursor.execute(query, (id_evaluacion,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener evaluación por ID: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()


def db_eliminar_nota_bd(id_nota):
    conexion = get_db()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        query = "DELETE FROM notas WHERE id = %s"
        cursor.execute(query, (id_nota,))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al eliminar nota: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()