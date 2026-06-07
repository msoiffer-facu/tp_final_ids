from services.config import BACKEND_URL
import requests

def obtener_cursos():
    try:
        # response = requests.get(f"{BACKEND_URL}/cursos/cursos")
        # cursos = response.json()
        cursos = [
        {
            "anio": 2026,
            "cuatrimestre": "1",
            "id": 1,
            "modificacion": "nose",
            "nombre": "clase 12"
        },
        {
            "anio": 2026,
            "cuatrimestre": "2",
            "id": 2,
            "modificacion": "nose",
            "nombre": "clase 12b"
        },
        {
            "anio": 2025,
            "cuatrimestre": "1",
            "id": 3,
            "modificacion": "nose",
            "nombre": "clase 1"
        },
        {
            "anio": 2025,
            "cuatrimestre": "2",
            "id": 4,
            "modificacion": "nose",
            "nombre": "clase 4"
        },
        {
            "anio": 2024,
            "cuatrimestre": "1",
            "id": 5,
            "modificacion": "ninguna",
            "nombre": "curso 15"
        }
        ]
    except:
        cursos = []
    return cursos

def obtener_curso_con_nombre(nombre):
    try:
        response = requests.get(f"{BACKEND_URL}/asistencia")
        clases_p = response.json()
    except:
        clases_p = []
    return clases_p
