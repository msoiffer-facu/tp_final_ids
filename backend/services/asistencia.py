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
        'pedir_asistencia': clase['pedir_asistencia']
    }

def listar_clases():
    """Retorna todas las clases."""
    return [construir_clase_p_dto(a) for a in obtener_clases_p()]