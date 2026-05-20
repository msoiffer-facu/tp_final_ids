import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root_pass",
        database="tp_final_ids_db",
        port=3306
    )