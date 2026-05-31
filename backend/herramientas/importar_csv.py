import csv
import io
from herramientas.validaciones_alumnos import validar_data_alumno

def importar_alumnos_csv(archivo):
    alumnos = []
    errores = []
    faltantes = []

    try:
        contenido = archivo.read().decode("utf-8-sig")

        reader = csv.DictReader(io.StringIO(contenido))

        if reader.fieldnames is None:
            return {"error": "CSV vacio"}
        
        columnas_obligatorias = [
            "nombre",
            "apellido",
            "email",
            "padron",
            "abandono"
        ]

        headers = [
            columna.strip().lower()
            for columna in reader.fieldnames
            ]

        for columna in columnas_obligatorias:
            if columna not in headers:
                faltantes.append(columna)

        if faltantes:
            return {"error": f"Faltan columnas: {', '.join(faltantes)}"}

        padrones = set()
        emails = set()

        for index, fila in enumerate(reader, start=2):

            if not any(fila.values()):
                continue

            errores_fila = []

            alumno_fila = validar_data_alumno(fila)

            errores_fila = alumno_fila["errores"]

            if alumno_fila["padron"] in padrones:
                errores_fila.append("padron duplicado")
            if alumno_fila["email"] in emails:
                errores_fila.append("email duplicado")

            if errores_fila:
                errores.append(f"Fila {index}: {', '.join(errores_fila)}")
                continue

            alumno = {
                "nombre": alumno_fila["nombre"],
                "apellido": alumno_fila["apellido"],
                "email": alumno_fila["email"],
                "padron": alumno_fila["padron"],
                "abandono": alumno_fila["abandono"],
                "estado": True
                }
            alumnos.append(alumno)
            padrones.add(alumno_fila["padron"])
            emails.add(alumno_fila["email"])

    except Exception as err:
        return {"error": str(err)}

    return {
        "alumnos": alumnos,
        "errores": errores
    }
