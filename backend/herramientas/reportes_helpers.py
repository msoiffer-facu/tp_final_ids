def normalize_text(value):
    if value is None:
        return ""
    return str(value)


def parse_bool(value):
    if value is None:
        return None
    value = str(value).strip().lower()
    if value in {"1", "true", "si", "yes", "y", "s"}:
        return True
    if value in {"0", "false", "no", "n"}:
        return False
    return None


def build_alumno_filters(params, columns, join_equipos):
    filters = []
    values = []

    nombre = params.get("nombre")
    apellido = params.get("apellido")
    equipo = params.get("equipo")
    aprobado = parse_bool(params.get("aprobado"))

    if nombre and "nombre" in columns:
        filters.append("LOWER(a.nombre) LIKE %s")
        values.append(f"%{nombre.lower()}%")
    if apellido and "apellido" in columns:
        filters.append("LOWER(a.apellido) LIKE %s")
        values.append(f"%{apellido.lower()}%")
    if equipo and join_equipos:
        filters.append("LOWER(e.nombre) LIKE %s")
        values.append(f"%{equipo.lower()}%")
    if aprobado is not None and "aprobado" in columns:
        if aprobado:
            filters.append("LOWER(CAST(a.aprobado AS CHAR)) IN ('1','true','si','yes','y','s')")
        else:
            filters.append("LOWER(CAST(a.aprobado AS CHAR)) NOT IN ('1','true','si','yes','y','s')")

    return filters, values


def build_equipos_filters(params, columns):
    filters = []
    values = []

    nombre = params.get("nombre")
    tutor = params.get("tutor")

    if nombre and "nombre" in columns:
        filters.append("LOWER(nombre) LIKE %s")
        values.append(f"%{nombre.lower()}%")
    if tutor and "tutor" in columns:
        filters.append("LOWER(tutor) LIKE %s")
        values.append(f"%{tutor.lower()}%")

    return filters, values
