import mysql.connector
from mysql.connector import Error
from config import Config

def conectar():
    """Establece la conexión con la base de datos joel_piel."""
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
    """Crea un cursor. Por defecto devuelve diccionarios (ideal para Flask)."""
    if conexion and conexion.is_connected():
        return conexion.cursor(dictionary=diccionario)
    return None

# --- GESTIÓN DE USUARIOS ---
def registrar_usuario(nombre, email, password_hash, rol='cliente'):
    """Inserta un nuevo usuario en la base de datos."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            sql = "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)"
            valores = (nombre, email, password_hash, rol)
            cursor.execute(sql, valores)
            db.commit()
            return True
        except Error as e:
            print(f"Error al registrar usuario: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return False

# --- GESTIÓN DE INVENTARIO (NUEVO) ---
 
def registrar_producto(nombre, precio, stock, imagen_url, id_categoria, descripcion=''):
    """Inserta un nuevo bolso en el inventario con categoría y descripción."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            sql = """INSERT INTO productos (nombre, precio, stock, imagen_url, Id_categoria, descripcion) 
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (nombre, precio, stock, imagen_url, id_categoria, descripcion))
            db.commit()
            return True
        except Exception as e:
            print(f"Error al registrar producto: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return False

def actualizar_stock_db(id_producto, nuevo_stock):
    """Actualiza la cantidad de stock de un producto específico."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            sql = "UPDATE productos SET stock = %s WHERE id_producto = %s"
            cursor.execute(sql, (nuevo_stock, id_producto))
            db.commit()
            return True
        except Error as e:
            print(f"Error al actualizar stock: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return False