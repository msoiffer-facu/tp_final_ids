from datetime import datetime

def calcular_clases_mes(clases):
    ahora = datetime.now()
    total_clases = 0
    errores = 0

    for clase in clases:
        fecha_texto = clase.get('fecha')
        if not fecha_texto:
            continue
        try:
            fecha = fecha_texto.split(' ')[0]
            _, mes, anio = fecha.split('/')
            if mes == f'0{ahora.month}' and anio == f'{(ahora.year % 100)}':
                total_clases += 1
        except ValueError:
            errores += 1
            continue
    fecha = clases[1].get('fecha')
    _, mes, anio = fecha.split('/')
    return total_clases

def obtener_clases_presenciales():
    clases_p = [
        {
            "id": "1",
            "curso": {
                "id":1,
                "nombre":"curso 3b",
                "total_alumnos":40,
                "presentes":10,
            },
            "fecha": "15/05/26 15:35",
            "estado":"en_proceso",
            "pedir_asistencia": True,
        },
        {
            "id": "2",
            "curso": {
                "id":1,
                "nombre":"curso 4a",
                "total_alumnos":25,
                "presentes":10,
            },
            "fecha": "14/05/26 21:35",
            "estado":"completado",
            "pedir_asistencia": False,
        },
        {
            "id": "3",
            "curso": {
                "id":1,
                "nombre":"curso 12c",
                "total_alumnos":30,
            },
            "fecha": "14/05/26 13:02",
            "estado":"pendiente",
            "pedir_asistencia": True,
        },
        {
            "id": "4",
            "curso": {
                "id":1,
                "nombre":"curso 14l",
                "total_alumnos":80,
            },
            "fecha": "14/04/26 13:02",
            "estado":"pendiente",
            "pedir_asistencia": False,
        },
        {
            "id": "5",
            "curso": {
                "id":1,
                "nombre":"curso 1g",
                "total_alumnos":25,
            },
            "fecha": "14/04/26 13:02",
            "estado":"pendiente",
            "pedir_asistencia": True,
        },
    ]
    return clases_p