from datetime import datetime
import requests

from services.config import BACKEND_URL

def obtener_clases_presenciales():
    try:
        response = requests.get(f"{BACKEND_URL}/asistencia")
        clases_p = response.json()
    except:
        clases_p = []
    return clases_p