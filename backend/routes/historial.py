from flask import Blueprint, jsonify, request

from services.historial import (
    guardar_historial,
    obtener_historial
)

historial_bp = Blueprint("historial", __name__)
"""
 historial: acciones -> cuando un profe modifica a un alumno o a un curso

 tabla de agus??
 
 se repite el abm de alumnos en views

 id de clase precensial, nomrbre del curso hora de la asistencia

 agregarle boton para asignarle un curso al alumno


"""


def subir_al_historial():
#if para cada opcion
 pass

def modificar_historial():
 pass