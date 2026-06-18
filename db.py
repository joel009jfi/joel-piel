import mysql.connector  # Driver oficial de MySQL para Python
from mysql.connector import Error
from config import Config  # Credenciales y configuración de la app


def conectar():
    """Abre y retorna una conexión a la BD usando credenciales de Config."""
    try:
        conexion = mysql.connector.connect(
            host=Config.DB_HOST,        # Dirección del servidor MySQL
            user=Config.DB_USER,        # Usuario de la BD
            password=Config.DB_PASSWORD, # Contraseña del usuario
            database=Config.DB_NAME,    # Nombre de la base de datos
            charset='utf8mb4',          # Soporte para caracteres especiales (tildes, emojis)
            collation='utf8mb4_general_ci'  # Regla de comparación de texto
        )
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error crítico al conectar a MySQL: {e}")
        return None


def obtener_cursor(conexion, diccionario=True):
    """Crea un cursor sobre una conexión existente.
    Con diccionario=True devuelve filas como dicts (ideal para Jinja2)."""
    if conexion and conexion.is_connected():
        return conexion.cursor(dictionary=diccionario)
    return None
