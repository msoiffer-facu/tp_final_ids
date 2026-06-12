import requests
from services.config import BACKEND_URL

def obtener_alumnos(pagina=1, busqueda="", abandono=""):
    response = requests.get(f"{BACKEND_URL}/alumnos", params={"pagina": pagina, "busqueda": busqueda, "abandono": abandono})
    data = response.json()

    return {
        "status_code": response.status_code,
        "data": {
            "alumnos": data.get("alumnos", []),
            "total": data.get("total", 0),
            "limit": data.get("limit", 10),
            "total_pages": data.get("total_pages", 1)
        }
    }

def actualizar_alumno(id, datos):
    response = requests.put(f"{BACKEND_URL}/alumnos/{id}",json=datos)
    return {
        "status_code": response.status_code,
        "data": response.json()
    }

def eliminar_alumno_service(id):
    response = requests.delete(f"{BACKEND_URL}/alumnos/{id}")
    
    return {
        "status_code": response.status_code,
        "data": response.json()
    } 

def importar_csv_service(file):
    response = requests.post( f"{BACKEND_URL}/alumnos/importar",files={"file": (file.filename, file.stream, file.content_type)})
    return {
        "status_code": response.status_code,
        "data": response.json()
    }

def crear_alumno(datos):
    response = requests.post(f"{BACKEND_URL}/alumnos", json=datos)
    return {
        "status_code": response.status_code,
        "data": response.json()
    }

def obtener_alumno(id):
    response = requests.get(f"{BACKEND_URL}/alumnos/{id}")
    
    return {
        "status_code": response.status_code,
        "data": response.json()
    }

def obtener_equipos_alumno(id):
    response = requests.get(
        f"{BACKEND_URL}/equipos/alumno/{id}"
    )

    return {
        "status_code": response.status_code,
        "data": response.json()
    }


def obtener_notas_alumno(id):
    response = requests.get(
        f"{BACKEND_URL}/notas/alumno/{id}"
    )

    return {
        "status_code": response.status_code,
        "data": response.json()
    }


def obtener_asistencias_alumno(id):
    response = requests.get(f"{BACKEND_URL}/asistencia/alumno/{id}")

    try:
        data = response.json()

    except Exception:
        return {"status_code": response.status_code, "data": []}

    return {"status_code": response.status_code,"data": data
    }