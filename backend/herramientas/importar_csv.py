import csv
import io
from herramientas.validaciones_alumnos import validar_convertir_padron, validar_email, validar_convertir_booleano, validar_convertir_string

def importar_alumnos_csv(archivo):
    alumnos = []
    errores = []
    faltantes = []
    try:
        
        contenido = archivo.read().decode("utf-8-sig")

        reader = csv.DictReader(io.StringIO(contenido))

        if reader.fieldnames is None:
            return {
                "error": "CSV vacio"
            }
        
        
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

            try:
                nombre = validar_convertir_string(fila["nombre"])
                apellido = validar_convertir_string(fila["apellido"])
                email = fila["email"]
                padron = validar_convertir_padron(fila["padron"])
                abandono = validar_convertir_booleano(fila["abandono"])

                if nombre is None:
                    errores_fila.append("nombre invalido")

                if apellido is None:
                    errores_fila.append("apellido invalido")

                if not validar_email(email):
                    errores_fila.append("email invalido")
                elif email in emails:
                    errores_fila.append("email duplicado")

                if padron is None:
                    errores_fila.append("padron invalido")
                else:
                    if padron in padrones:
                        errores_fila.append("padron duplicado")

                if abandono is None:
                    errores_fila.append("abandono invalido")

                if errores_fila:
                    errores.append(f"Fila {index}: {', '.join(errores_fila)}")
                    continue

                alumno = {
                    "nombre": nombre,
                    "apellido": apellido,
                    "email": email,
                    "padron": padron,
                    "abandono": abandono,
                    "estado": True
                }
                alumnos.append(alumno)
                
                padrones.add(padron)
                emails.add(email)

            except Exception as err:
                errores.append(f"Fila {index}: {str(err)}")

    except Exception as err:
        return {"error": str(err)}

    return {
        "alumnos": alumnos,
        "errores": errores
    }
