from flask import Blueprint, jsonify, request
from dbs.db_historial import crear_historial, obtener_historial, registrar_historial

historial_bp = Blueprint("historial", __name__)

"""
cambiar boton de alm como prof"""
@historial_bp.route("/", methods=["GET"])
def listar_historial():
    try:
        limit = request.args.get("limit", 5, type=int)
        historial = obtener_historial(limit)
        return jsonify({"historial": historial}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@historial_bp.route("/", methods=["POST"])
def crear_historial_manual():
    data = request.get_json() or {}

    usuario = data.get("usuario", "Sistema")
    accion = data.get("accion")
    modulo = data.get("modulo")

    if not accion or not modulo:
        return jsonify({"error": "accion y modulo requeridos"}), 400

    try:
        registrar_historial(usuario, accion, modulo)
        return jsonify({"mensaje": "evento registrado"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500