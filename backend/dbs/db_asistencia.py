import json
import mysql.connector
import secrets
from datetime import datetime, timedelta
import io
import qrcode
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from db import get_db


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "correoprobar6@gmail.com"
SMTP_PASSWORD = "voph xnfy xtmy bovm"


def obtener_clases_p():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clase_presencial")
    clases_p = cursor.fetchall()
    cursor.close()
    return clases_p

def crear_clase_p( curso):
    db = get_db()
    print(curso['id'])
    cursor = db.cursor()
    fecha = datetime.now()
    cursor.execute(
        "INSERT INTO clase_presencial (curso_id, fecha) VALUES (%s, %s)",
        (curso['id'], fecha)
    )
    db.commit()
    cursor.close()

def buscar_clase_p(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clase_presencial WHERE id = %s",(id,))
    clase = cursor.fetchone()
    cursor.close()
    return clase

def actualizar_clase_p(id, fecha, curso_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE clase_presencial SET fecha = %s, curso_id = %s WHERE id = %s",
        (fecha, curso_id, id),
    )
    db.commit()
    cursor.close()

def eliminar_clase_p(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM clase_presencial WHERE id = %s", (id,))
    db.commit()
    cursor.close()

def crear_asistencia_alumnos(alumnos, clase_id):
    db = get_db()
    cursor = db.cursor()

    datos = [(alumno['id'], clase_id) for alumno in alumnos]

    query = "INSERT INTO asistencias (alumno_id, clase_presencial_id) VALUES (%s, %s)"
    cursor.executemany(query, datos)
    db.commit()
    cursor.close()

def crear_token_alumno(alumnos):
    db = get_db()
    cursor = db.cursor()

    ahora = datetime.now()
    fecha_expiracion = ahora + timedelta(hours=2)

    datos = []
    tokens_creados = []

    for alumno in alumnos:
        token = secrets.token_hex(16)
        datos.append((token, alumno['id'], fecha_expiracion, 0))
        tokens_creados.append({
            "alumno_id": alumno['id'],
            "nombre":alumno['nombre'],
            "email":alumno['email'],
            "token": token,
        })

    query = "INSERT INTO tokens_asistencia (token, alumno_id, fecha_expiracion, utilizado) VALUES (%s, %s, %s, %s)"
    cursor.executemany(query, datos)
    db.commit()
    cursor.close()
    return tokens_creados


def crear_enviar_qr_alumnos(datos):
    try:
        token = datos['token']
        email_destino = datos['email']
        nombre_alumno = datos['nombre']

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(token)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer_memoria = io.BytesIO()
        img.save(buffer_memoria, format="PNG")
        buffer_memoria.seek(0)

        mensaje = MIMEMultipart()
        mensaje['From'] = SMTP_USER
        mensaje['To'] = email_destino
        mensaje['Subject'] = f"Tu Token de Asistencia - {nombre_alumno}"

        cuerpo_html = f"""
        <html>
            <body>
                <h2>¡Hola, {nombre_alumno}!</h2>
                <p>Presentá el siguiente código QR al profesor en el aula para registrar tu asistencia del día de hoy.</p>
                <p><i>Este qr expira en 2 horas.</i></p>
                <br>
                <p>Saludos,<br>clase de Introduccion al desarrollo de software</p>
            </body>
        </html>
        """
        mensaje.attach(MIMEText(cuerpo_html, 'html'))

        adjunto_qr = MIMEImage(buffer_memoria.read(), name="asistencia_qr.png")
        mensaje.attach(adjunto_qr)

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)

        server.sendmail(SMTP_USER, email_destino, mensaje.as_string())
        server.quit()
    except Exception as e:
        print(f"Falló el procesamiento para un alumno: {e}")

def asistencia_enviada(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE clase_presencial SET pedir_asistencia = 1 WHERE id = %s",
        (id,),
    )
    db.commit()
    cursor.close()


def comprobar_token(token_ingresado, clase_id):
    respuesta = ""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM tokens_asistencia WHERE token = %s AND utilizado = 0 AND fecha_expiracion > CURRENT_TIMESTAMP;",
        (token_ingresado,),
    )
    token = cursor.fetchone()

    if token:
        cursor.execute(
            "UPDATE tokens_asistencia SET utilizado = 1 WHERE id = %s",
            (token["id"],),
        )
        cursor.execute(
            "UPDATE asistencias SET presente = 1 WHERE alumno_id = %s AND clase_presencial_id = %s;",
            (token["alumno_id"], clase_id,),
        )
        db.commit()
        respuesta = "Se a verificado el token correctamente"
    else:
        respuesta = "token no encontrado"
    cursor.close()

    if not respuesta:
        respuesta = "El token no se encuentra en la tabla o ya no es valido"

    return respuesta


#TODO: cambiar la siguiente funcion a un archivo de curso y no dejarlo en el repository de asistencia
def buscar_curso(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos WHERE id = %s",(id,))
    curso = cursor.fetchone()
    cursor.close()
    return curso

def obtener_cursos():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cursos")
    cursos = cursor.fetchall()
    cursor.close()
    return cursos

def listar_alumnos_por_curso(curso_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT a.* FROM alumnos a
        INNER JOIN alumnos_curso ac ON a.id = ac.alumnos_id
        WHERE ac.curso_id = %s
    """
    cursor.execute(query, (curso_id,))
    curso = cursor.fetchall()
    cursor.close()
    return curso