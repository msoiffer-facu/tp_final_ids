from flask import redirect, url_for
from flask import Blueprint, request, jsonify
from flask import render_template
from dbs.db_evaluaciones import (
    db_crear_evaluacion_bd,
    db_eliminar_evaluacion_bd,
    db_obtener_todas_las_evaluaciones,
    db_modificar_evaluacion_bd,
    db_obtener_tipo_de_evaluacion_bd,
    db_crear_tipo_de_evaluacion_bd,
    db_eliminar_tipo_de_evaluacion_bd,
    db_modificar_tipo_de_evaluacion_bd,
    db_obtener_todos_los_cursos_bd,
    db_obtener_notas_por_evaluacion_bd,
    db_eliminar_nota_bd,
    db_obtener_evaluacion_por_id_bd
)

evaluaciones_bp = Blueprint('evaluaciones', __name__)

@evaluaciones_bp.route('/', methods=['GET'])
def vista_evaluaciones():
    print(">>> EL SERVIDOR ESTÁ LEYENDO LA RUTA PRINCIPAL DE EVALUACIONES <<<")
    lista = db_obtener_todas_las_evaluaciones()
    return render_template('evaluaciones/evaluaciones.html', evaluaciones=lista)


@evaluaciones_bp.route('/api', methods=['POST'])
def crear_evaluacion():
    data = request.get_json()
    if not data or 'titulo' not in data or 'fecha' not in data or 'tipo_id' not in data or 'curso_id' not in data:
        return jsonify({"mensaje": "faltan datos obligatorios (titulo, fecha, tipo_id, curso_id)"}), 400

    nuevo_id = db_crear_evaluacion_bd(data['titulo'], data['fecha'], data['tipo_id'], data['curso_id'])
    if nuevo_id:
        return jsonify({"mensaje": "Evaluación creada correctamente", "id": nuevo_id}), 201
    return jsonify({"mensaje": "Error al crear la evaluación"}), 500

@evaluaciones_bp.route('/crear', methods=['GET'])
def formulario_crear_evaluacion():
    tipos = db_obtener_tipo_de_evaluacion_bd()

    cursos = db_obtener_todos_los_cursos_bd()

    return render_template('evaluaciones/formulario_evaluacion.html' , tipos=tipos, cursos=cursos)


@evaluaciones_bp.route('/eliminar/<int:id_evaluacion>', methods=['POST'])
def eliminar_evaluacion(id_evaluacion):
    exito = db_eliminar_evaluacion_bd(id_evaluacion)
    if exito:
        return redirect(url_for("evaluaciones.vista_evaluaciones"))
    else:
        return "No se puede eliminar la evaluación", 404
    

@evaluaciones_bp.route('/api', methods=['GET'])
def obtener_evaluaciones():
    lista = db_obtener_todas_las_evaluaciones()
    return jsonify(lista), 200    


@evaluaciones_bp.route('/<int:id_evaluacion>', methods=['PUT'])
def modificar_evaluacion(id_evaluacion):
    data = request.get_json()
    if not data or not any(key in data for key in ['titulo', 'fecha', 'tipo_id', 'curso_id']):
        return jsonify({"mensaje": "no se proporcionaron datos para modificar"}), 400
    
    exito = db_modificar_evaluacion_bd(
        id_evaluacion,
          data.get('titulo'),
          data.get('fecha'),
          data.get('tipo_id'),
          data.get('curso_id')
    )
    if exito:
        return jsonify({"mensaje": "evaluacion modificada correctamente"}), 200
    return jsonify({"mensaje": " no se encontro la evaluacion o no se pudo modificar"}), 404



@evaluaciones_bp.route('/tipos', methods=['POST'])
def crear_tipo_de_evaluacion():
    data = request.get_json()
    if not data or 'nombre' not in data:
        return jsonify({"mensaje": "falta el campo obligatorio 'nombre'"}), 400
    exito = db_crear_tipo_de_evaluacion_bd(data['nombre'])
    if exito:
        return jsonify({"mensaje": "tipo de evaluacion creado correctamente"}), 201
    return jsonify({"mensaje": "error al crear el tipo de evaluacion"}), 500

@evaluaciones_bp.route('/tipos/<int:id_tipo>', methods=['DELETE'])
def eliminar_tipo_de_evaluacion_bd(id_tipo):
    exito = db_eliminar_tipo_de_evaluacion_bd(id_tipo)
    if exito:
        return jsonify({"mensaje": "tipo de evaluacion eliminado correctamente"}), 200
    return jsonify({"mensaje": "no se encontro el tipo de evaluacion o contiene evaluaciones asociadas"}), 404

@evaluaciones_bp.route('/tipos', methods=['GET'])
def obtener_tipos_de_evaluacion():
    tipos = db_obtener_tipo_de_evaluacion_bd()
    return jsonify(tipos), 200


@evaluaciones_bp.route('/tipos/<int:id_tipo>', methods=['PUT'])
def modificar_tipo_de_evaluacion_bd(id_tipo):
    data = request.get_json()
    if not data or 'nombre' not in data:
        return jsonify({"mensaje": "falta el campo obligatorio 'nombre'"}), 400
    

    exito = db_modificar_tipo_de_evaluacion_bd(id_tipo, data['nombre'])
    if exito:
        return jsonify({"mensaje": "tipo de evaluacion modificado correctamente"}), 200
    return jsonify({"mensaje": "no se encontro el tipo de evaluacion o no se pudo modificar"}), 404

@evaluaciones_bp.route('/modificar/<int:id_evaluacion>', methods=['GET'])
def vista_modificar_evaluacion(id_evaluacion):

    tipos = db_obtener_tipo_de_evaluacion_bd()
    cursos = db_obtener_todos_los_cursos_bd()
    return render_template('evaluaciones/formulario_evaluacion.html', id_evaluacion=id_evaluacion, tipos=tipos, cursos=cursos)


@evaluaciones_bp.route('/notas/<int:id_evaluacion>', methods=['GET'])
def carga_notas(id_evaluacion):
    evaluacion = db_obtener_evaluacion_por_id_bd(id_evaluacion)
    datos_notas = db_obtener_notas_por_evaluacion_bd(id_evaluacion)
    print("CONTENIDO DE DATOS_NOTAS:", datos_notas)
    titulo = evaluacion['titulo'] if evaluacion else 'Evaluación Desconocida'
    return render_template('evaluaciones/notas.html', notas=datos_notas, evaluacion_titulo=titulo, id_evaluacion=id_evaluacion)


@evaluaciones_bp.route('/notas/editar/<int:id_nota>', methods=['GET', 'POST'])
def vista_editar_nota(id_nota):
    return "Editando la nota con ID: " + str(id_nota)

@evaluaciones_bp.route('/notas/eliminar/<int:id_nota>/<int:id_evaluacion>', methods=['POST'])
def eliminar_nota(id_nota, id_evaluacion):
    exito = db_eliminar_nota_bd(id_nota)
    
    if exito:
        print(f"Nota {id_nota} eliminada con éxito.")
    
    return redirect(url_for('evaluaciones.carga_notas', id_evaluacion=id_evaluacion))