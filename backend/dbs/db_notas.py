from db import get_db

def crear_nota_db(alumno_id, evaluacion_id, nota_alumno, estado):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""INSERT INTO notas (alumno_id, evaluacion_id, nota_alumno, estado) VALUES (%s, %s, %s, %s)""", (alumno_id, evaluacion_id, nota_alumno, estado))

        conn.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        conn.close()


def obtener_notas_db():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT notas.id, notas.nota_alumno, notas.estado, alumnos.nombre, alumnos.apellido, evaluaciones.titulo, evaluaciones.fecha, tipos_evaluacion.nombre 
            FROM notas
            JOIN alumnos
                ON notas.alumno_id = alumnos.id
            JOIN evaluaciones
                ON notas.evaluacion_id = evaluaciones.id
            JOIN tipos_evaluacion
                ON evaluaciones.tipo_id = tipos_evaluacion.id""")

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def obtener_notas_alumno_db(alumno_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
      cursor.execute("""SELECT notas.id, notas.nota_alumno, notas.estado, alumnos.nombre, alumnos.apellido, evaluaciones.titulo, evaluaciones.fecha, tipos_evaluacion.nombre, 
                     cursos.nombre AS curso, cursos.cuatrimestre, cursos.anio
                      FROM notas
                     JOIN alumnos
                      ON notas.alumno_id = alumnos.id
                     JOIN evaluaciones
                      ON notas.evaluacion_id = evaluaciones.id
                     JOIN tipos_evaluacion
                      ON evaluaciones.tipo_id = tipos_evaluacion.id
                     JOIN cursos
                      ON evaluaciones.curso_id = cursos.id 
                     WHERE notas.alumno_id = %s""", (alumno_id,))

      return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def obtener_notas_equipo_db(equipo_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""SELECT notas.id, notas.nota_alumno, notas.estado, alumnos.padron, alumnos.nombre, alumnos.apellido, evaluaciones.titulo, evaluaciones.fecha,
            tipos_evaluacion.nombre, equipos.nombre FROM notas
            JOIN alumnos
                ON notas.alumno_id = alumnos.id
            JOIN equipo_alumnos
                ON alumnos.id = equipo_alumnos.alumno_id
            JOIN equipos
                ON equipo_alumnos.equipo_id = equipos.id
            JOIN evaluaciones
                ON notas.evaluacion_id = evaluaciones.id
            JOIN tipos_evaluacion
                ON evaluaciones.tipo_id = tipos_evaluacion.id
            WHERE equipos.id = %s""", (equipo_id,))

        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def modificar_nota_db(nota_id, nota_alumno, estado):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""UPDATE notas SET nota_alumno = %s, estado = %s WHERE id = %s""", (nota_alumno, estado, nota_id))

        conn.commit()
        return cursor.rowcount

    finally:
        cursor.close()
        conn.close()


def eliminar_nota_db(nota_id):
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""DELETE FROM notas WHERE id = %s""", (nota_id,))

        conn.commit()
        return cursor.rowcount

    finally:
        cursor.close()
        conn.close()