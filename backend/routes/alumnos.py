from flask import Blueprint, jsonify, request
from herramientas.importar_csv import importar_alumnos_csv
from herramientas.validaciones_alumnos import  validar_data_alumno, importar_alumnos_db
from dbs.db_alumnos import db_get_alumnos, db_get_alumno_id, db_delete_alumno, db_create_alumno, db_update_alumno
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

    resultado = importar_alumnos_csv(file)

    if "error" in resultado:
        return jsonify({"error": resultado["error"]}), 400 

    try:

        resultado_db = importar_alumnos_db(resultado["alumnos"])

    except mysql.connector.Error:
        return jsonify({"error": "Error de base de datos"}), 500

    return jsonify({
        "insertados": resultado_db["insertados"],
        "errores": resultado["errores"] + resultado_db["errores"]
    }), 200


@alumnos_bp.route("/", methods=["GET"])
def obtener_alumnos():
    try:
        alumnos = db_get_alumnos()

    except mysql.connector.Error:
        return jsonify({"error": "Error de base de datos"}), 500

    return jsonify(alumnos), 200


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

        db_create_alumno(alumno_validado["nombre"], alumno_validado["apellido"], alumno_validado["email"], alumno_validado["padron"], alumno_validado["abandono"], alumno_validado["estado"])

    except mysql.connector.Error:
        return jsonify({"error": "Error de base de datos"}), 500

    return jsonify({"mensaje": "Alumno creado"}), 201