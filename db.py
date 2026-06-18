import mysql.connector
from mysql.connector import Error
from config import Config


def conectar():
    try:
        conexion = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error crítico al conectar a MySQL: {e}")
        return None


def obtener_cursor(conexion, diccionario=True):
    if conexion and conexion.is_connected():
        return conexion.cursor(dictionary=diccionario)
    return None
