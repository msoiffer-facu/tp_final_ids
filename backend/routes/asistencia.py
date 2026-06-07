from flask import Blueprint, jsonify, request, url_for
import math
import threading
import asyncio

from dbs.db_asistencia import *
from dbs.db_cursos import db_get_curso_by_id
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
        curso = db_get_curso_by_id(curso_id)
    except Exception as e:
        return f'Error interno al buscar el curso: {e}',500

    if not curso:
        return "El curso con el que quiere hacer la clase no existe", 404
    
    serv_asistencia.crear_asistencia(curso)

    return "", 201

@asistencia_bp.route("/<id>", methods=['PUT'])
def modificar_clase_presencial(id):
    data = request.get_json()
    fecha = data.get("fecha")
    curso_id = data.get("curso_id")

    if fecha is None or curso_id is None:
        return "fecha y curso_id son requeridos",404

    clase_p = serv_asistencia.buscar_asistencias(id)

    if not clase_p:
        return "Usuario no encontrado",404

    serv_asistencia.actualizar_asistencia(id, fecha, curso_id)

    clase_p = serv_asistencia.buscar_asistencias(id)

    return jsonify(clase_p),204

@asistencia_bp.route("/<id>", methods=['DELETE'])
def eliminar_clase_presencial(id):
    if id is None:
        return "El id es necesario",404
    
    clase_p = serv_asistencia.buscar_asistencias(id)

    if not clase_p:
        return "clase presencial no encontrada",404

    eliminar_asistencia(id)

    return "", 204

@asistencia_bp.route("/<id>/alumnos", methods=['GET'])
def details_clase_presencial(id):
    if id is None:
        return "El id es necesario",404

    alumnos = serv_asistencia.listar_alumnos_asistencia_clase(id)

    if not alumnos:
        return "clase presencial no encontrada",404

    return jsonify(alumnos), 200



@asistencia_bp.route("/pedir-asistencia", methods=['POST'])
def create_asistencia():
    data = request.get_json()
    id_clase = data.get("id_clase_p")

    clase = serv_asistencia.buscar_asistencias(id_clase)

    if not clase:
        return "No existe una clase con ese id", 404

    tokens = serv_asistencia.pedir_asistencia(clase, id_clase)
 
    # Lanzar el envío en background sin bloquear la respuesta HTTP
    thread = threading.Thread(target=serv_asistencia._enviar_qr_en_thread, args=(tokens, id_clase))
    thread.daemon = True
    thread.start()
 
    return "Se creo la asistencia correctamente", 200


@asistencia_bp.route("/verificar-asistencia", methods=['POST'])
def verificar_asistencia():
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    clase_id = data.get("clase_id")

    if not token:
        return "Token no enviado", 400

    respuesta = serv_asistencia.revisar_token(token,clase_id)

    return respuesta, 200

@asistencia_bp.route("/finalizar-clase", methods=['POST'])
def finalizar_clase():
    data = request.get_json()
    clase_id = data.get("clase_id")

    if not clase_id:
        return "ID de clase no proporcionado", 400

    serv_asistencia.finalizar_tomar_asistencia(clase_id)

    return "Clase finalizada correctamente", 200