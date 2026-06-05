from flask import Blueprint, jsonify, request, url_for
import math
import threading

from dbs.db_asistencia import *
import services.asistencia as serv_asistencia
from concurrent.futures import ThreadPoolExecutor

asistencia_bp = Blueprint("asistencia", __name__)

@asistencia_bp.route("/promedio", methods=['GET'])
def promedio_asistencia():
    try:
        promedio_asistencia = obtener_promedio_asistencia()
    except Exception:
        return 'Error al calcular el promedio de asistencia',500

    return jsonify({"promedio_asistencia": promedio_asistencia}, ), 200

@asistencia_bp.route("/", methods=['GET'])
def get_clase_presencial():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    curso_id = request.args.get("curso", type=int)

    if page <= 0:
        return "El page debe ser mayor a 0",404
    if per_page <= 0:
        return "El per_page debe ser mayor a 0",404
    try:
        clases_p,total_registros = serv_asistencia.listar_clases(page, per_page, curso_id)
    except Exception as err:
        return jsonify(err.__cause__),500

    if not clases_p:
        return jsonify([]),200

    return jsonify(
        {
            "clases_presenciales":clases_p,
            "total": total_registros,
            "page": page,
            "per_page": per_page,
            "total_pages": math.ceil(total_registros / per_page)
        }
    ),200

@asistencia_bp.route("/en-proceso", methods=['GET'])
def get_clases_en_proceso():
    try:
        clases_ep = serv_asistencia.listar_clases_en_proceso()
    except Exception as err:
        return jsonify(err.__cause__),500

    if not clases_ep:
        return jsonify([]),200

    return jsonify(clases_ep),200

@asistencia_bp.route("/", methods=['POST'])
def create_clase_presencial():
    data = request.get_json()
    curso_id = data.get("curso_id")

    if curso_id is None:
        return "curso_id es requerido",404

    try:
        curso = buscar_curso(curso_id)
    except Exception as e:
        return f'Error interno al buscar el curso: {e}',500

    if not curso:
        return "El curso con el que quiere hacer la clase no existe", 404
    try:
        crear_clase_p(curso)
    except Exception:
        return"Error interno al crear la clase presencial",500

    return "", 201

@asistencia_bp.route("/<id>", methods=['PUT'])
def modificar_clase_presencial(id):
    data = request.get_json()
    fecha = data.get("fecha")
    curso_id = data.get("curso_id")

    if fecha is None or curso_id is None:
        return "fecha y curso_id son requeridos",404

    try:
        clase_p = buscar_clase_p(id)
    except Exception:
        return"Error interno al bucar la clase presencial",500

    if not clase_p:
        return "Usuario no encontrado",404

    try:
        #TODO: hacer funcion en db para crear la clase presncial
        actualizar_clase_p(id, fecha, curso_id)
    except Exception:
        return"Error interno al actualizar la clase presencial",500

    return jsonify(clase_p),204

@asistencia_bp.route("/<id>", methods=['DELETE'])
def eliminar_clase_presencial(id):
    if id is None:
        return "El id es necesario",404

    try:
        clase_p = buscar_clase_p(id)
    except Exception:
        return "Error interno al obtener la clase",500

    if not clase_p:
        return "clase presencial no encontrada",404

    try:
        eliminar_clase_p(id)
    except Exception:
        return "Error interno al eliminar la clase",500
    return "", 204

@asistencia_bp.route("/<id>/alumnos", methods=['GET'])
def details_clase_presencial(id):
    if id is None:
        return "El id es necesario",404

    try:
        alumnos = serv_asistencia.listar_alumnos_asistencia_clase(id)
    except Exception:
        return "Error interno al obtener la clase",500

    if not alumnos:
        return "clase presencial no encontrada",404

    return jsonify(alumnos), 200

def enviar_qr_async(tokens, id_clase):
    """Envía los QR de forma asincrónica"""
    try:
        for token in tokens:
            if validar_mail(token['email']):
                crear_enviar_qr_alumnos(token)
        print(f"QR enviados exitosamente para la clase {id_clase}")
    except Exception as e:
        print(f"Error al enviar QR de forma asincrónica: {e}")

@asistencia_bp.route("/pedir-asistencia", methods=['POST'])
def create_asistencia():
    data = request.get_json()
    id_clase = data.get("id_clase_p")

    try:
        clase = buscar_clase_p(id_clase)
    except Exception:
        return "Error interno al buscar la clase",500

    if not clase:
        return "No existe una clase con ese id", 404

    try:
        alumnos = listar_alumnos_por_curso(clase["curso_id"])
    except Exception:
        return "Error interno al listar a los alumnos del curso",500

    if not alumnos:
        return "No hay alumnos en esta clase",404

    try:
        asistencia_enviada(id_clase)
    except Exception:
        return "Error interno al cambiar el estado de la asistencia",500

    tokens = crear_token_alumno(alumnos)

    try:
        crear_asistencia_alumnos(alumnos, id_clase, tokens)
    except Exception:
        return "Error interno al crear las asistencias",500

    # Enviar QR de forma asincrónica en un thread separado
    thread = threading.Thread(target=enviar_qr_async, args=(tokens, id_clase))
    thread.daemon = True
    thread.start()

    return "Se creo la asistencia correctamente",200

@asistencia_bp.route("/verificar-asistencia", methods=['POST'])
def verificar_asistencia():
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    clase_id = data.get("clase_id")

    if not token:
        return "Token no enviado", 400

    try:
        respuesta = comprobar_token(token, clase_id)
    except Exception as e:
        return f'Error al revisar el token. {e}', 500

    return respuesta, 200

@asistencia_bp.route("/finalizar-clase", methods=['POST'])
def finalizar_clase():
    data = request.get_json()
    clase_id = data.get("clase_id")

    if not clase_id:
        return "ID de clase no proporcionado", 400

    try:
        terminar_clase(clase_id)
    except Exception as e:
        return f'Error al finalizar la clase. {e}', 500

    return "Clase finalizada correctamente", 200