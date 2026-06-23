import requests
from services.alumnos_service import calcular_promedio_alumno
from services.config import BACKEND_URL
from services.login import backend_request

def obtener_dashboard_estadisticas():
    try:
        total_alumnos =backend_request("GET", "/alumnos/todos").json()
        print(total_alumnos)
        equipos = backend_request("GET", "/equipos").json()
        total_notas = backend_request("GET", "/notas").json()
        promediar_response = backend_request("GET", "/asistencia/promedio").json()

        promedio_asistencia = promediar_response.get("promedio_asistencia", 0)

        alumnos_promocionados = 0
        for alumno in total_alumnos:
            print(alumno["id"])
            notas = backend_request("GET", f"/notas/alumno/{alumno['id']}").json()
            resultado = calcular_promedio_alumno(notas)
            
            if resultado["promociona"]:
                alumnos_promocionados += 1

        return {
            "status_code": 200,
            "data": {
                "total_alumnos": len(total_alumnos),
                "total_equipos": len(equipos),
                "notas_subidas": len(total_notas),
                "prom_asistencia": round(promedio_asistencia, 2),
                "alumnos_promocionados": alumnos_promocionados
            }
        }
    except Exception as e:
        return {"status_code": 500, "data": {"error": str(e)}}



def obtener_dashboard_historial(limit=5):
    try:
        resultado = backend_request("GET", "/historial", params={"limit": limit})
        if resultado.status_code != 200:
            return []

        data = resultado.json()
        return data.get("historial", []) if isinstance(data, dict) else []
    
    except Exception:
        return []
   