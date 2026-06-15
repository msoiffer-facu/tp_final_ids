import dbs.db_asistencia as db_asistencia
from dbs.db_cursos import get_total_alumnos_curso
import asyncio

def construir_clase_p_dto(clase):
    curso = db_asistencia.buscar_curso(clase['curso_id'])
    return {
        'id':   clase['id'],
        'fecha':   clase['fecha'].strftime('%Y-%m-%d %H:%M:%S'),
        'curso': {
            'id': curso['id'],
            'nombre': curso['nombre'],
            'total_alumnos': get_total_alumnos_curso(curso['id'])
        },
        'pedir_asistencia': clase['pedir_asistencia'],
        'finalizada': clase['finalizada'],
    }

def contruir_alumno_asistencia_dto(alumno):
    return {
        'padron': alumno['padron'],
        'nombre': alumno['nombre'],
        'apellido': alumno['apellido'],
        'email': alumno['email'],
        'estado': alumno['estado'],
        'presente': alumno['presente'],
        'asistencia_registrada': alumno['asistencia_registrada'].strftime('%Y-%m-%d %H:%M:%S') if alumno['asistencia_registrada'] else None
    }


def listar_clases(page, per_page, curso_id=None):
    """Retorna todas las clases."""
    clases,total = db_asistencia.obtener_clases_p(page, per_page, curso_id)
    return [construir_clase_p_dto(a) for a in clases], total

def listar_clases_en_proceso():
    """Retorna todas las clases en proceso."""
    clases = db_asistencia.obtener_clases_en_proceso()
    return [construir_clase_p_dto(a) for a in clases]

def listar_alumnos_asistencia_clase(clase_id):
    try:
        alumnos = db_asistencia.obtener_alumnos_asistencia_clase(clase_id)
    except Exception:
        return "Error interno al obtener la clase",500
    return [contruir_alumno_asistencia_dto(alumno) for alumno in alumnos]

def validar_mail(mail):
    return '@' in mail and '.' in mail

def crear_asistencia(curso):
    try:
        db_asistencia.crear_clase_p(curso)
    except Exception:
        return"Error interno al crear la clase presencial",500

def buscar_asistencias(id_clase_p):
    clase_p = []
    try:
        clase_p = db_asistencia.buscar_clase_p(id_clase_p)
    except Exception:
        return"Error interno al bucar la clase presencial",500
    
    return clase_p

def actualizar_asistencia(id, fecha, curso_id):
    try:
        db_asistencia.actualizar_clase_p(id, fecha, curso_id)
    except Exception:
        return"Error interno al actualizar la clase presencial",500

def eliminar_asistencia(id):
    try:
        db_asistencia.eliminar_clase_p(id)
    except Exception:
        return "Error interno al eliminar la clase",500

def finalizar_tomar_asistencia(clase_id):
    try:
        db_asistencia.terminar_clase(clase_id)
    except Exception as e:
        return f'Error al finalizar la clase. {e}', 500

def revisar_token(token, clase_id):
    respuesta = []
    try:
        respuesta = db_asistencia.comprobar_token(token, clase_id)
    except Exception as e:
        return f'Error al revisar el token. {e}', 500
    return respuesta

def pedir_asistencia(clase, id_clase):
    try:
        alumnos = db_asistencia.listar_alumnos_por_curso(clase["curso_id"])
    #except Exception:
     #   return "Error interno al listar a los alumnos del curso",500
    except Exception as e:
        print("ERROR CREANDO ASISTENCIAS:", e)
        raise
    if not alumnos:
        return "No hay alumnos en esta clase",404

    try:
        db_asistencia.asistencia_enviada(id_clase)
    except Exception:
        return "Error interno al cambiar el estado de la asistencia",500

    tokens = db_asistencia.crear_token_alumno(alumnos)

    try:
        db_asistencia.crear_asistencia_alumnos(alumnos, id_clase, tokens)
    #except Exception:
     #   return "Error interno al crear las asistencias", 500
    except Exception as e:
        print("ERROR CREANDO TOKENS", e)
        raise
    return tokens

def _enviar_qr_en_thread(tokens, id_clase):
    """
    Función que corre en un thread separado.
    Crea su propio event loop para no interferir con el de Flask.
    """
    try:
        tokens_validos = [t for t in tokens if validar_mail(t['email'])]
        if not tokens_validos:
            print(f"No hay tokens válidos para la clase {id_clase}")
            return
 
        # Crear un event loop nuevo para este thread (no reutilizar el de Flask)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(db_asistencia.enviar_multiples_correos_async(tokens_validos))
            print(f"QR enviados exitosamente para la clase {id_clase}")
        finally:
            loop.close()
    except Exception as e:
        print(f"Error al enviar QR para la clase {id_clase}: {e}")