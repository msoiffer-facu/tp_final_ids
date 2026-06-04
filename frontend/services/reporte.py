from services.login import backend_request


def obtener_reporte_alumnos(filtros=None):
    resp = backend_request("GET", "/api/reportes/alumnos", params=filtros or {}, timeout=10)
    if not resp.ok:
        raise RuntimeError(f"Error al obtener reporte de alumnos: {resp.status_code}")
    return resp.json()


def obtener_reporte_equipos(filtros=None):
    resp = backend_request("GET", "/api/reportes/equipos", params=filtros or {}, timeout=10)
    if not resp.ok:
        raise RuntimeError(f"Error al obtener reporte de equipos: {resp.status_code}")
    return resp.json()


def obtener_estadisticas():
    resp = backend_request("GET", "/api/reportes/estadisticas", timeout=10)
    if not resp.ok:
        raise RuntimeError(f"Error al obtener estadísticas: {resp.status_code}")
    return resp.json()
