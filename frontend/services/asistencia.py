from datetime import datetime
import requests

from services.config import BACKEND_URL

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