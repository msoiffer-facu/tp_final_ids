import csv
import io


def generar_csv_alumnos(alumnos):
    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "nombre",
        "apellido",
        "email",
        "padron",
        "abandono"
    ])

    for alumno in alumnos:
        writer.writerow([
            alumno["nombre"],
            alumno["apellido"],
            alumno["email"],
            alumno["padron"],
            alumno["abandono"]
        ])

    return output.getvalue()