import requests
from services.config import BACKEND_URL
from services.login import backend_request

def obtener_alumnos(pagina=1, busqueda="", abandono=""):
    response = backend_request("GET", "/alumnos", params={"pagina": pagina, "busqueda": busqueda, "abandono": abandono})
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

def calcular_promedio_alumno(notas): 
 if not notas:
    return {
        "promedio": 0,
        "promociona": False,
        "curso": None,
        "cuatrimestre": None,
        "anio": None
        }

 anio_actual = 0

 for nota in notas:
    if nota["anio"] > anio_actual:
        anio_actual = nota["anio"]

 cuatrimestre_actual = "1"

 for nota in notas:
    if nota["anio"] == anio_actual:
        if nota["cuatrimestre"] == "2":
            cuatrimestre_actual = "2"

 curso_actual = None

 for nota in notas:
    if (nota["anio"] == anio_actual and nota["cuatrimestre"] == cuatrimestre_actual): 
        curso_actual = nota["curso"]
        break

 suma = 0
 cantidad = 0

 for nota in notas:
    if (nota["anio"] == anio_actual and nota["cuatrimestre"] == cuatrimestre_actual and nota["curso"] == curso_actual):
        suma += float(nota["nota_alumno"])
        cantidad += 1

 promedio = suma / cantidad if cantidad > 0 else 0

 return {"promedio": round(promedio, 2), "promociona": promedio >= 7, "curso": curso_actual, "cuatrimestre": cuatrimestre_actual, "anio": anio_actual}

def actualizar_alumno(id, datos):
    response = backend_request("PUT", f"/alumnos/{id}", json=datos)
    return {
        "status_code": response.status_code,
        "data": response.json()
    }

def eliminar_alumno_service(id):
    response = backend_request("DELETE", f"/alumnos/{id}")
    
    print("status:", response.status_code)
    print("texto:", response.text)
    
    return {
        "status_code": response.status_code,
        "data": response.json()
    } 

def importar_csv_service(file):
    response = backend_request(
        "POST",
        "/alumnos/importar",
        files={"file": (file.filename, file.read(), file.content_type)}
    )

    print("STATUS:", response.status_code)
    print("RESPUESTA:")
    print(response.text)

    try:
        data = response.json()
    except Exception:
        data = {"error": response.text}

    return {
        "status_code": response.status_code,
        "data": data
    }

def crear_alumno(datos):
    response = backend_request("POST", "/alumnos", json=datos)

    print("STATUS:", response.status_code)
    print("TEXT:", response.text)

    return {
        "status_code": response.status_code,
        "data": response.json()
    }
def obtener_alumno(id):
    response = backend_request("GET", f"/alumnos/{id}")
    
    return {
        "status_code": response.status_code,
        "data": response.json()
    }

def obtener_equipos_alumno(id):
    response = backend_request("GET", f"/equipos/alumno/{id}")

    return {
        "status_code": response.status_code,
        "data": response.json()
    }


def obtener_notas_alumno(id):
    response = backend_request("GET", f"/notas/alumno/{id}")

    return {
        "status_code": response.status_code,
        "data": response.json()
    }


def obtener_asistencias_alumno(id):
    response = backend_request("GET", f"/asistencia/alumno/{id}")

    try:
        data = response.json()

    except Exception:
        return {"status_code": response.status_code, "data": []}

    return {"status_code": response.status_code,"data": data["data"]
    }