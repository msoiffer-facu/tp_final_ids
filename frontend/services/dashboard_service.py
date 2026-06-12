import requests
from services.config import BACKEND_URL

def obtener_dashboard():
    try:
        alumnos = requests.get(f"{BACKEND_URL}/alumnos").json()
        equipos = requests.get(f"{BACKEND_URL}/equipos").json()
        notas = requests.get(f"{BACKEND_URL}/notas").json()

        promedio_asistencia = requests.get(
            f"{BACKEND_URL}/asistencia/promedio"
        ).json().get("promedio_asistencia", 0)

        alumnos_promocionados = 0

        for nota in notas:
            if isinstance(nota, dict) and nota.get("estado") == "PROMOCIONADO":
                alumnos_promocionados += 1

        return {
            "status_code": 200,
            "data": {
                "total_alumnos": len(alumnos),
                "total_equipos": len(equipos),
                "notas_subidas": len(notas),
                "prom_asistencia": round(promedio_asistencia, 2),
                "alumnos_promocionados": alumnos_promocionados
            }
        }

    except requests.RequestException as e:
        return {
            "status_code": 500,
            "data": {
                "error": str(e)
            }
        }