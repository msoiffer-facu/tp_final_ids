from flask import Blueprint, jsonify, request

from services.historial import (
    guardar_historial,
    obtener_historial
)

historial_bp = Blueprint("historial", __name__)
"""

 falta:
 csv exportar y cambiar su html
 boton eliminar alumno boton editar alumno
 historial 
 tabla de agus
 acciones -> cuando un profe modifica a un alumno o a un curso

"""


def subir_al_historial():
#if para cada opcion
 pass

def modificar_historial():
 pass