import os

import mysql.connector


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "tp_final_user"),
        password=os.getenv("DB_PASSWORD", "tp_final_pass"),
        database=os.getenv("DB_NAME", "tp_final_db"),
        auth_plugin=os.getenv("DB_AUTH_PLUGIN", "mysql_native_password"),
    )
