import re

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