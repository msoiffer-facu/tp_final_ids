from datetime import datetime
from flask import flash
import requests

from services.config import BACKEND_URL
from services.login import backend_request

def obtener_clases_presenciales(page=1, per_page=10, curso_id=None):
    try:
        params = {"page": page, "per_page": per_page}
        if curso_id is not None:
            params["curso"] = curso_id
        response = requests.get(f"{BACKEND_URL}/asistencia", params=params)
        clases_p = response.json()
    except:
        clases_p = []
    return clases_p

def obtener_clases_en_proceso():
    try:
        response = requests.get(f"{BACKEND_URL}/asistencia/en-proceso")
        clases_ep = response.json()
    except:
        clases_ep = []
    return clases_ep

def obtener_alumnos_asistencia_clase(clase_id):
    try:
        response = requests.get(f"{BACKEND_URL}/asistencia/{clase_id}/alumnos")
        alumnos = response.json()
    except:
        alumnos = []
    return alumnos

def crear_asistencia(curso_id_form):
    data = {"curso_id": curso_id_form}
    response = backend_request("POST", "/asistencia", json=data)

    if response.ok:
        flash("Asistencia creada correctamente.", "success")
    else:
        flash(f"Error al crear la asistencia: {response.text}", "error")

    return response

def pedir_asistencia(clase_id):
    data = {"id_clase_p": clase_id}
    response = backend_request("POST", "/asistencia/pedir-asistencia", json=data)

    if response.ok:
        flash("QR de asistencia enviado correctamente.", "success")
    else:
        flash(f"Error al enviar el QR de asistencia: {response.text}", "error")

    return response

def finalizar_clase(clase_id):
    response = backend_request("POST", "/asistencia/finalizar-clase", json={"clase_id": clase_id})

    if response.ok:
        flash("Clase finalizada correctamente.", "success")
    else:
        flash(f"Error al finalizar la clase: {response.text}", "error")

    return response

def verificar_asistencia(token, clase_id):
   return backend_request("POST", "/asistencia/verificar-asistencia", json={"token": token, "clase_id": clase_id})