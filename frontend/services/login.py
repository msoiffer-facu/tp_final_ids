from flask import session, flash, redirect, url_for

def usuario_logueado():
    return session.get("user") is not None

def guardar_sesion(token: str, usuario: dict):
    session["token"] = token
    session["user"] = usuario

def limpiar_sesion():
    session.pop("token", None)
    session.pop("user", None)