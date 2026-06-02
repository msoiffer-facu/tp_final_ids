from flask import Blueprint, jsonify, request, url_for
from herramientas.importar_csv import importar_alumnos_csv
from herramientas.validaciones_alumnos import  validar_data_alumno
from dbs.db_alumnos import db_get_alumnos, db_get_alumno_id, db_delete_alumno, db_create_alumno, db_update_alumno, comprobar_alumno_existente, cargar_alumnos_db
import os
import mysql.connector

alumnos_bp = Blueprint("alumnos", __name__)

@alumnos_bp.route("/importar", methods=["POST"])
def importar_lista():
    file = request.files.get("file")

    if file is None:
        return jsonify({"error": "Archivo faltante"}), 400

    name = file.filename
    extension=os.path.splitext(name)[1].lower()

    if extension != '.csv':
        return jsonify({"error": "Formato invalido"}), 400

    try:
        resultado = importar_alumnos_csv(file)

        if "error" in resultado:
            return jsonify({"error": resultado["error"]}), 400

        resultado_db = cargar_alumnos_db(resultado["alumnos"])
    except mysql.connector.Error:
        return jsonify({"error": "Error de base de datos"}), 500
    except Exception as err:
        return jsonify({"error": str(err)}), 500

    return jsonify({
        "insertados": resultado_db["insertados"],
        "existentes": resultado_db["existentes"],
        "errores": resultado["errores"]
    }), 200


@alumnos_bp.route("/", methods=["GET"])
def obtener_alumnos():
    pagina = request.args.get("pagina", 1, type=int)
    busqueda = request.args.get("busqueda", "", type=str).strip()
    abandono = request.args.get("abandono", "", type=str).strip()

    if pagina < 1:
        return jsonify({"error": "Pagina invalida"}), 400

    limit = 10
    offset = (pagina - 1) * limit
    
    try:
        alumnos_pagina, total_registros = db_get_alumnos(offset, limit, busqueda, abandono)

    except mysql.connector.Error:
        return jsonify({"error": "Error de base de datos"}), 500

    return jsonify({
        "alumnos": alumnos_pagina,
        "total": total_registros,
        "pagina": pagina,
        "limit": limit,
        "total_pages": (total_registros + limit - 1) // limit
    }), 200


@alumnos_bp.route("/<int:id>", methods=["GET"])
def obtener_alumno(id):
    try:
        alumno = db_get_alumno_id(id)
        if not alumno:
            return jsonify({"error": "Alumno no encontrado"}), 404

    except mysql.connector.Error:
        return jsonify({"error": "Error de base de datos"}), 500
    
    return jsonify(alumno), 200


@alumnos_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_alumno(id):
    try:
        alumno = db_get_alumno_id(id)
        if not alumno:
            return jsonify({"error": "Alumno no encontrado"}), 404

        db_delete_alumno(id)

    except mysql.connector.Error:
        return jsonify({"error": "Error de base de datos"}), 500

    return jsonify({"mensaje": "Alumno eliminado"}), 200


@alumnos_bp.route("/<int:id>", methods=["PUT"])
def modificar_alumno(id):
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Body faltante"}), 400
    
    try:
        if not db_get_alumno_id(id):
            return jsonify({"error": "Alumno no encontrado"}), 404

        alumno_validado = validar_data_alumno(data, id)
        if alumno_validado["errores"]:
            return jsonify({"errores": alumno_validado["errores"]}), 400

        errores_db = comprobar_alumno_existente(alumno_validado["email"], alumno_validado["padron"], id)
        if errores_db:
            return jsonify({"errores": errores_db}), 400

        db_update_alumno(id, alumno_validado["nombre"], alumno_validado["apellido"], alumno_validado["email"], alumno_validado["padron"], alumno_validado["abandono"], alumno_validado["estado"])

    except mysql.connector.Error:
        return jsonify({"error": "Error de base de datos"}), 500

    return jsonify({"mensaje": "Alumno modificado"}), 200


@alumnos_bp.route("/", methods=["POST"])
def crear_alumno():
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Body faltante"}), 400

    try:
        alumno_validado = validar_data_alumno(data)
        if alumno_validado["errores"]:
            return jsonify({"errores": alumno_validado["errores"]}), 400
        
        errores_db = comprobar_alumno_existente(alumno_validado["email"], alumno_validado["padron"])
        if errores_db:
            return jsonify({"errores": errores_db}), 400

        db_create_alumno(alumno_validado["nombre"], alumno_validado["apellido"], alumno_validado["email"], alumno_validado["padron"], alumno_validado["abandono"], alumno_validado["estado"])

    except mysql.connector.Error:
        return jsonify({"error": "Error de base de datos"}), 500

    return jsonify({"mensaje": "Alumno creado"}), 201