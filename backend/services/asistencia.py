from dbs.db_asistencia import *
from dbs.db_cursos import get_total_alumnos_curso

def construir_clase_p_dto(clase):
    curso = buscar_curso(clase['curso_id'])
    return {
        'id':   clase['id'],
        'fecha':   clase['fecha'],
        'curso': {
            'id': curso['id'],
            'nombre': curso['nombre'],
            'total_alumnos': get_total_alumnos_curso(curso['id'])
        },
        'pedir_asistencia': clase['pedir_asistencia'],
        'finalizada': clase['finalizada'],
    }

# def contruir_alumno_asistencia_dto(alumno):
#     return {
#         'id': alumno['id'],
#         'nombre': alumno['nombre'],
#         'apellido': alumno['apellido'],
#         'email': alumno['email'],
#         'presente': alumno['presente'],
#         'asistencia_registrada': alumno['asistencia_registrada']
#     }


def listar_clases(page, per_page, curso_id=None):
    """Retorna todas las clases."""
    clases,total = obtener_clases_p(page, per_page, curso_id)
    return [construir_clase_p_dto(a) for a in clases], total

def listar_clases_en_proceso():
    """Retorna todas las clases en proceso."""
    clases = obtener_clases_en_proceso()
    return [construir_clase_p_dto(a) for a in clases]

def listar_alumnos_asistencia_clase(clase_id):
    alumnos = obtener_alumnos_asistencia_clase(clase_id)
    return alumnos

def validar_mail(mail):
    return '@' in mail and '.' in mail