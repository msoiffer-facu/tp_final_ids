from dbs.db_asistencia import *

def construir_clase_p_dto(clase):
    curso = buscar_curso(clase['curso_id'])
    return {
        'id':   clase['id'],
        'fecha':   clase['fecha'],
        'curso': {
            'id': curso['id'],
            'nombre': curso['nombre']
        },
        'pedir_asistencia': clase['pedir_asistencia'],
        'finalizada': clase['finalizada']
    }

def listar_clases(page, per_page, curso_id=None):
    """Retorna todas las clases."""
    clases,total = obtener_clases_p(page, per_page, curso_id)
    return [construir_clase_p_dto(a) for a in clases], total

def listar_clases_en_proceso():
    """Retorna todas las clases en proceso."""
    clases = obtener_clases_en_proceso()
    return [construir_clase_p_dto(a) for a in clases]