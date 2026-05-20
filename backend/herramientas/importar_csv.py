import csv
from backend.herramientas.validaciones import validar_alumno 

def improtar_alumnos_csv(archivo):
    alumnos=[]
    errores = []
    with open(archivo, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        columnas_obligatorias = [
            "nombre",
            "apellido",
            "email",
            "padron"
        ]

    # validar columnas
        for field in columnas_obligatorias:
            if field not in reader.fieldnames:
                return {
                    "error": f"Falta la columna {field}"
                }
        for number, row in enumerate(reader, start=2):

            try:
            # validar vacíos
                if not row["nombre"]:
                    errores.append(
                       f"Fila {number}: nombre vacío"
                    )
                    continue
                if not row["email"]:
                    errores.append(
                        f"Fila {number}: email vacío"
                    )
                    continue

            # validar padrón
                try:
                    padron = int(row["padron"])
                except ValueError:
                    errores.append(
                        f"Fila {numero_fila}: padrón inválido"
                    )
                    continue

                alumno = {
                    "nombre": row["nombre"].strip(),
                    "apellido": row["apellido"].strip(),
                    "email": row["email"].strip(),
                    "padron": padron
                }

                alumnos.append(alumno)

            except Exception as e:

                errores.append(
                    f"Fila {numero_fila}: {str(e)}"
                )

    return {
        "alumnos": alumnos,
        "errores": errores
    }