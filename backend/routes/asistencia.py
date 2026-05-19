from flask import Blueprint, jsonify, request, url_for

asistencia_bp = Blueprint("asistencia", __name__)

@asistencia_bp.route("/", methods=['GET'])
def get_clase_presencial():
    return 200

@asistencia_bp.route("/", methods=['POST'])
def create_clase_presencial():
    return 200

@asistencia_bp.route("/<id>", methods=['DELETE'])
def eliminar_clase_presencial(id):
    return 200

@asistencia_bp.route("/<id>", methods=['PUT'])
def modificar_clase_presencial(id):
    return 200

@asistencia_bp.route("/pedir-asistencia", methods=['POST'])
def create_asistencia():
    data = request.get_json()
    id_clase = data.get("id_clase_p")

    # TODO: crear funcion en db que me devuelva una fila de la tabla clase_presencial en base al id
    clase = buscar_clase(id_clase)

    #TODO: crear funcion en db que me devuelva los alumnos de la tabla alumnos que tengan x curso
    alumnos = listar_alumnos_por_curso(clase.curso)

    #TODO: crear funcion en db que inserte una nueva fila (por cada alumno) en la tabla asistencias con el id del alumno y el id de la clase presencial (por defecto la columna presente=false)
    crear_asistencia_alumnos(alumnos, id_clase)

    #TODO: tengo que crear los tokens para cada alumno que se guardan en la tabla tokens_asistencia
    #TODO: ver como limpiar la tabla tokens_asistencia cada x cantidad de tiempo
    tokens = crear_token_alumno(alumnos)

    #TODO: aca tengo que crear un qr en base a cada token de cada alumno y enviarselos por su email
    enviar_qr_alumnos(alumnos, token)
    return 200

