import csv

def importar_alumnos_csv(archivo):
    alumnos = []
    errores = []
    try:
        
        # convertir bytes a texto utf-8
        lineas = archivo.stream.read().decode("utf-8").splitlines()

        reader = csv.DictReader(lineas)

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

        for columna in columnas_obligatorias:
            if columna not in reader.fieldnames:
                return {"error": f"Falta la columna {columna}"}

        for index, fila in enumerate(reader, start=2):
            try:
                if not fila["nombre"]:
                    errores.append(f"Fila {index}: nombre vacio")
                    continue
                if not fila["apellido"]:
                    errores.append(f"Fila {index}: apellido vacio")
                    continue
                if not fila["email"]:
                    errores.append(f"Fila {index}: email vacio")
                    continue

                try:
                    padron = int(fila["padron"])
                except (ValueError, TypeError):
                    errores.append(f"Fila {index}: padron invalido")
                    continue

                abandono_texto = fila["abandono"].strip().lower()
                if abandono_texto == "true":
                    abandono = True
                elif abandono_texto == "false":
                    abandono = False
                else:
                    errores.append(f"Fila {index}: abandono invalido")
                    continue

                alumno = {
                    "nombre": fila["nombre"].strip(),
                    "apellido": fila["apellido"].strip(),
                    "email": fila["email"].strip(),
                    "padron": padron,
                    "abandono": abandono,
                    "estado": True
                }
                alumnos.append(alumno)

            except Exception as err:
                errores.append(f"Fila {index}: {str(err)}")

    except Exception as err:
        return {"error": str(err)}

    return {
        "alumnos": alumnos,
        "errores": errores
    }
