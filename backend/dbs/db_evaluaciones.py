from db import get_db


# ─── TIPOS DE EVALUACIÓN ───

def db_obtener_tipos_evaluacion():
    conexion = get_db()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre FROM tipos_evaluacion ORDER BY nombre")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener tipos de evaluación: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


def db_obtener_tipo_evaluacion(id_tipo):
    conexion = get_db()
    if conexion is None: return None
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre FROM tipos_evaluacion WHERE id = %s", (id_tipo,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener tipo de evaluación: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()


def db_crear_tipo_evaluacion(nombre):
    conexion = get_db()
    if conexion is None: return None
    cursor = conexion.cursor()
    try:
        cursor.execute("INSERT INTO tipos_evaluacion (nombre) VALUES (%s)", (nombre,))
        conexion.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error al crear tipo de evaluación: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()


def db_actualizar_tipo_evaluacion(id_tipo, nombre):
    conexion = get_db()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        cursor.execute("UPDATE tipos_evaluacion SET nombre = %s WHERE id = %s", (nombre, id_tipo))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar tipo de evaluación: {e}")
        return False
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


# ─── EVALUACIONES ───

def db_obtener_todas_las_evaluaciones(page=1, per_page=10, tipo_id=None, curso_id=None):
    conexion = get_db()
    if conexion is None: return [], 0
    cursor = conexion.cursor(dictionary=True)
    try:
        conditions = []
        params = []
        if tipo_id:
            conditions.append("e.tipo_id = %s")
            params.append(tipo_id)
        if curso_id:
            conditions.append("e.curso_id = %s")
            params.append(curso_id)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        cursor.execute(f"SELECT COUNT(*) as total FROM evaluaciones e {where}", params)
        total = cursor.fetchone()["total"]

        offset = (page - 1) * per_page
        cursor.execute(f"""
            SELECT e.id, e.titulo, e.fecha, e.tipo_id, e.curso_id,
                   t.nombre AS tipo_nombre,
                   c.nombre AS curso_nombre
            FROM evaluaciones e
            JOIN tipos_evaluacion t ON e.tipo_id = t.id
            JOIN cursos c ON e.curso_id = c.id
            {where}
            ORDER BY e.fecha DESC
            LIMIT %s OFFSET %s
        """, params + [per_page, offset])
        return cursor.fetchall(), total
    except Exception as e:
        print(f"Error al obtener evaluaciones: {e}")
        return [], 0
    finally:
        cursor.close()
        conexion.close()


def db_obtener_evaluacion(id_evaluacion):
    conexion = get_db()
    if conexion is None: return None
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT e.id, e.titulo, e.fecha, e.tipo_id, e.curso_id,
                   t.nombre AS tipo_nombre,
                   c.nombre AS curso_nombre
            FROM evaluaciones e
            JOIN tipos_evaluacion t ON e.tipo_id = t.id
            JOIN cursos c ON e.curso_id = c.id
            WHERE e.id = %s
        """, (id_evaluacion,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener evaluación: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()


def db_crear_evaluacion(titulo, fecha, tipo_id, curso_id):
    conexion = get_db()
    if conexion is None: return None
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "INSERT INTO evaluaciones (titulo, fecha, tipo_id, curso_id) VALUES (%s, %s, %s, %s)",
            (titulo, fecha, tipo_id, curso_id)
        )
        conexion.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error al crear evaluación: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()


def db_actualizar_evaluacion(id_evaluacion, titulo, fecha, tipo_id, curso_id):
    conexion = get_db()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        cursor.execute(
            "UPDATE evaluaciones SET titulo = %s, fecha = %s, tipo_id = %s, curso_id = %s WHERE id = %s",
            (titulo, fecha, tipo_id, curso_id, id_evaluacion)
        )
        conexion.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error al actualizar evaluación: {e}")
        return False
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


# ─── NOTAS DE EVALUACIÓN ───

def db_obtener_notas_evaluacion(id_evaluacion):
    conexion = get_db()
    if conexion is None: return []
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT a.id AS alumno_id, a.padron, a.nombre, a.apellido,
                   n.id AS nota_id, n.nota_alumno, n.estado
            FROM alumnos_curso ac
            JOIN alumnos a ON ac.alumnos_id = a.id
            LEFT JOIN notas n ON a.id = n.alumno_id AND n.evaluacion_id = %s
            WHERE ac.curso_id = (SELECT curso_id FROM evaluaciones WHERE id = %s)
            ORDER BY a.apellido, a.nombre
        """, (id_evaluacion, id_evaluacion))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener notas: {e}")
        return []
    finally:
        cursor.close()
        conexion.close()


def db_guardar_notas_evaluacion(id_evaluacion, notas):
    conexion = get_db()
    if conexion is None: return False
    cursor = conexion.cursor()
    try:
        for nota in notas:
            alumno_id = nota["alumno_id"]
            nota_alumno = float(nota["nota_alumno"])

            if nota_alumno >= 7:
                estado = "PROMOCIONADO"
            elif nota_alumno >= 4:
                estado = "APROBADO"
            else:
                estado = "DESAPROBADO"

            cursor.execute(
                "SELECT id FROM notas WHERE alumno_id = %s AND evaluacion_id = %s",
                (alumno_id, id_evaluacion)
            )
            existing = cursor.fetchone()
            if existing:
                cursor.execute(
                    "UPDATE notas SET nota_alumno = %s, estado = %s WHERE alumno_id = %s AND evaluacion_id = %s",
                    (nota_alumno, estado, alumno_id, id_evaluacion)
                )
            else:
                cursor.execute(
                    "INSERT INTO notas (alumno_id, evaluacion_id, nota_alumno, estado) VALUES (%s, %s, %s, %s)",
                    (alumno_id, id_evaluacion, nota_alumno, estado)
                )

        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al guardar notas: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        conexion.close()
