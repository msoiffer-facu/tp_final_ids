import requests
from services.config import BACKEND_URL
from services.login import backend_request

def obtener_dashboard_estadisticas():
    try:
        alumnos = requests.get(f"{BACKEND_URL}/alumnos/todos").json()
        equipos = requests.get(f"{BACKEND_URL}/equipos").json()
        notas = requests.get(f"{BACKEND_URL}/notas").json()

        promedio_asistencia = requests.get(
            f"{BACKEND_URL}/asistencia/promedio"
        ).json().get("promedio_asistencia", 0)

        alumnos_promocionados = len([
            nota for nota in notas
            if isinstance(nota, dict) and nota.get("estado") == "PROMOCIONADO"
        ])

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


def obtener_dashboard_historial(limit=5):
    try:
        resultado = backend_request("GET", "/historial", params={"limit": limit})
        if resultado.status_code != 200:
            return []

        data = resultado.json()
        return data.get("historial", []) if isinstance(data, dict) else []
    except requests.RequestException:
        return []
    except ValueError:
        return []