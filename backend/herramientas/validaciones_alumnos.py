import re
from dbs.db_alumnos import db_buscar_dato_alumno, db_create_alumno

def validar_email(email):
    if not isinstance(email, str):
        return False
    
    patron = r"^[^@]+@[^@]+\.[^@]+$"

    return re.match(patron, email) is not None

def validar_convertir_padron(padron):
    try:
        padron = int(padron)
        if padron <= 0:
            return None
        return padron

    except (ValueError, TypeError):
        return None
    
def validar_convertir_booleano(valor):
    if isinstance(valor, bool):
        return valor
    
    if isinstance(valor, str):
        valor = valor.strip().lower()

    if valor in (1, "1", "true"):
        return True

    if valor in (0, "0", "false"):
        return False
    
    return None

def validar_convertir_string(valor):
    if not isinstance(valor, str):
        return None
    valor = valor.strip()

    if not valor:
        return None

    if valor.isdigit():
        return None

    return valor

def validar_data_alumno(data, id=None):
    errores = []

    nombre_validado = validar_convertir_string(data.get("nombre"))
    if nombre_validado is None:
        errores.append("nombre invalido")

    apellido_validado = validar_convertir_string(data.get("apellido"))
    if apellido_validado is None:
        errores.append("apellido invalido")

    if not validar_email(data.get("email")):
        errores.append("email invalido")

    padron_validado = validar_convertir_padron(data.get("padron"))
    if padron_validado is None:
        errores.append("padron invalido")

    abandono_validado = validar_convertir_booleano(data.get("abandono"))
    if abandono_validado is None:
        errores.append("abandono invalido")

    estado_validado = validar_convertir_booleano(data.get("estado"))

# Permitir que 'estado' sea opcional en formularios que no lo envían (ej. editar alumno desde frontend)
    if estado_validado is None:
        if data.get("estado") is None:
            estado_validado = True
        else:
            errores.append("estado invalido")

    alumno_padron = db_buscar_dato_alumno("padron", padron_validado, id)
    if alumno_padron:
        errores.append("padron ya registrado")

    alumno_email = db_buscar_dato_alumno("email", data.get("email"), id)
    if alumno_email:
        errores.append("email ya registrado")

    return {
        "nombre": nombre_validado,
        "apellido": apellido_validado,
        "email": data.get("email"),
        "padron": padron_validado,
        "abandono": abandono_validado,
        "estado": estado_validado,
        "errores": errores,
        "curso_id":data.get("curso_id")
    }

def validar_importacion_db(alumnos):
    errores_alumnos = []
    alumno_repeticion_email = db_buscar_dato_alumno("email", alumnos["email"], None)
    alumno_repeticion_padron = db_buscar_dato_alumno("padron", alumnos["padron"], None)

    if alumno_repeticion_email:
        errores_alumnos.append(f"email {alumnos['email']} ya registrado")

    if alumno_repeticion_padron:
        errores_alumnos.append(f"padron {alumnos['padron']} ya registrado")

    return {
        "errores": errores_alumnos
    }

def importar_alumnos_db(alumnos):
    errores = []
    insertados = 0

    for alumno in alumnos:

        validar_alumno = validar_importacion_db(alumno)

        if validar_alumno["errores"]:
            errores.extend(validar_alumno["errores"])
            continue

        
        db_create_alumno(
            alumno["nombre"],
            alumno["apellido"],
            alumno["email"],
            alumno["padron"],
            alumno["abandono"],
            alumno["estado"]
        )

        insertados += 1

    return {
        "insertados": insertados,
        "errores": errores
    }