from flask import Blueprint, jsonify, request, url_for

from routes.db_asistencia import *

asistencia_bp = Blueprint("asistencia", __name__)

# @asistencia_bp.route("/cursos", methods=['GET'])
# def get_cursos():
#     try:
#         #TODO: en db hacer la funcion obtener_clases_p()
#         cursos = obtener_cursos()
#     except Exception as e:
#         return jsonify(e.__cause__),500

#     return jsonify({"cursos" : cursos}),200

@asistencia_bp.route("/", methods=['GET'])
def get_clase_presencial():
    offset = request.args.get("_offset", 0, type=int)
    limit = request.args.get("_limit", 10, type=int)

    if limit <= 0 or limit > 100:
        return "El limite debe ser un numero entre 0 y 100",404
    if offset < 0:
        return "El offset no puede ser menor a 0"
    try:
        clases_p = obtener_clases_p()
    except Exception as err:
        return jsonify(err.__cause__),500

    if not clases_p:
        return jsonify({}),204

    total_registros = len(clases_p)

    prev_url = None
    prev_url = url_for(
        "asistencia.get_clase_presencial",
        _offset=max(0, offset - limit),
        _limit=limit,
        _external=True,
    )

    next_url = None
    if offset < total_registros - limit:
        next_url = url_for(
            "asistencia.get_clase_presencial",
            _offset=offset + limit,
            _limit=limit,
            _external=True,
        )
    else:
        next_url = url_for(
            "asistencia.get_clase_presencial",
            _offset=max(0, ((total_registros - 1) // limit) * limit),
            _limit=limit,
            _external=True,
        )
    return jsonify(
        {
            "clases_presenciales":clases_p,
            "links": {
                "_first": {
                    "href": url_for(
                        "asistencia.get_clase_presencial", _offset=0, _limit=limit, _external=True
                    )
                },
                "_prev": {"href": prev_url},
                "_next": {"href": next_url},
                "_last": {
                    "href": url_for(
                        "asistencia.get_clase_presencial",
                        _offset=max(0, ((total_registros - 1) // limit) * limit),
                        _limit=limit,
                        _external=True,
                    )
                },
            },
        }
    ),200

@asistencia_bp.route("/", methods=['POST'])
def create_clase_presencial():
    data = request.get_json()
    fecha = data.get("fecha")
    id_curso = data.get("id_curso")

    if fecha is None or id_curso is None:
        return "fecha y id_curso son requeridos",404

    try:
        curso = buscar_curso(id_curso)
    except Exception:
        return"Error interno al buscar el curso",500

    if not curso:
        return "El curso con el que quiere hacer la clase no existe", 404
    try:
        crear_clase_p(fecha, curso)
    except Exception:
        return"Error interno al crear la clase presencial",500

    return "", 201

@asistencia_bp.route("/<id>", methods=['PUT'])
def modificar_clase_presencial(id):
    data = request.get_json()
    fecha = data.get("fecha")
    id_curso = data.get("id_curso")

    if fecha is None or id_curso is None:
        return "fecha y id_curso son requeridos",404

    try:
        clase_p = buscar_clase_p(id)
    except Exception:
        return"Error interno al bucar la clase presencial",500

    if not clase_p:
        return "Usuario no encontrado",404

    try:
        #TODO: hacer funcion en db para crear la clase presncial
        actualizar_clase_p(id, fecha, id_curso)
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
        crear_asistencia_alumnos(alumnos, id_clase)
    except Exception:
        return "Error interno al crear las asistencias",500

    return jsonify(
        {
            "alumnos":alumnos
        }
    ),200

    # #TODO: tengo que crear los tokens para cada alumno que se guardan en la tabla tokens_asistencia
    # #TODO: ver como limpiar la tabla tokens_asistencia cada x cantidad de tiempo
    # tokens = crear_token_alumno(alumnos)

    # #TODO: aca tengo que crear un qr en base a cada token de cada alumno y enviarselos por su email
    # enviar_qr_alumnos(alumnos, token)
    return 200

@asistencia_bp.route("/verificar-asistencia", methods=['POST'])
def verificar_asistencia():
    data = request.get_json()
    token = data.get("token")

    comprobar_token()
    return 200