import requests

BASE_URL = "http://localhost:5000/alumnos"

def obtener_alumnos(pagina=1, busqueda="", abandono=""):
    response = requests.get(BASE_URL, params={"pagina": pagina, "busqueda": busqueda, "abandono": abandono})
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

def obtener_alumno(id):
    response = requests.get(f"{BASE_URL}/{id}")
    
    return {
        "status_code": response.status_code,
        "data": response.json()
    }

def actualizar_alumno(id, datos):
    response = requests.put(f"{BASE_URL}/{id}",json=datos)
    return {
        "status_code": response.status_code,
        "data": response.json()
    }

def eliminar_alumno(id):
    response = requests.delete(f"{BASE_URL}/{id}")
    
    return {
        "status_code": response.status_code,
        "data": response.json()
    } 

def importar_csv_service(file):
    response = requests.post( f"{BASE_URL}/importar",files={"file": (file.filename, file.stream, file.content_type)})
    return {
        "status_code": response.status_code,
        "data": response.json()
    }

