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

def guardar_carrito_db(Id_usuario, carrito_dict):
    """Guarda el carrito de sesión en la base de datos para un usuario."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM carrito WHERE Id_usuario = %s", (Id_usuario,))
            for id_producto, cantidad in carrito_dict.items():
                cursor.execute(
                    "INSERT INTO carrito (Id_usuario, id_producto, cantidad) VALUES (%s, %s, %s)",
                    (Id_usuario, int(id_producto), cantidad)
                )
            db.commit()
        except Error as e:
            print(f"Error al guardar carrito en DB: {e}")
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

def cargar_carrito_db(Id_usuario):
    """Carga el carrito desde la base de datos. Retorna dict {id_producto: cantidad}."""
    db = conectar()
    if db:
        try:
            cursor = obtener_cursor(db, diccionario=True)
            cursor.execute("SELECT id_producto, cantidad FROM carrito WHERE Id_usuario = %s", (Id_usuario,))
            filas = cursor.fetchall()
            return {str(fila['id_producto']): fila['cantidad'] for fila in filas}
        except Error as e:
            print(f"Error al cargar carrito desde DB: {e}")
            return {}
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return {}

def asegurar_tabla_carrito():
    """Crea la tabla carrito si no existe."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carrito (
                    id_carrito INT AUTO_INCREMENT PRIMARY KEY,
                    Id_usuario INT NOT NULL,
                    id_producto INT NOT NULL,
                    cantidad INT NOT NULL DEFAULT 1,
                    FOREIGN KEY (Id_usuario) REFERENCES usuarios(Id_usuario) ON DELETE CASCADE,
                    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
                )
            """)
            db.commit()
        except Error as e:
            print(f"Error al crear tabla carrito: {e}")
        finally:
            if db.is_connected():
                cursor.close()
                db.close()

# --- GESTIÓN DE CATEGORÍAS ---
def obtener_categorias():
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT Id_categoria, nombre_categoria FROM categorias ORDER BY Id_categoria")
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener categorías: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()

def crear_categoria(nombre):
    db = conectar()
    if not db:
        return False
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO categorias (nombre_categoria) VALUES (%s)", (nombre,))
        db.commit()
        return True
    except Error as e:
        print(f"Error crear categoría: {e}")
        return False
    finally:
        if db.is_connected():
            cursor.close()
            db.close()

def editar_categoria(id_categoria, nombre):
    db = conectar()
    if not db:
        return False
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE categorias SET nombre_categoria = %s WHERE Id_categoria = %s", (nombre, id_categoria))
        db.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error editar categoría: {e}")
        return False
    finally:
        if db.is_connected():
            cursor.close()
            db.close()

def eliminar_categoria(id_categoria):
    db = conectar()
    if not db:
        return False
    try:
        cursor = db.cursor()
        # Reasignar productos de esta categoría a 'Sin categoría' (id 1 como fallback)
        cursor.execute("UPDATE productos SET Id_categoria = 1 WHERE Id_categoria = %s", (id_categoria,))
        cursor.execute("DELETE FROM categorias WHERE Id_categoria = %s", (id_categoria,))
        db.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error eliminar categoría: {e}")
        return False
    finally:
        if db.is_connected():
            cursor.close()
            db.close()

def limpiar_carrito_db(Id_usuario):
    """Elimina todos los items del carrito en DB para un usuario."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM carrito WHERE Id_usuario = %s", (Id_usuario,))
            db.commit()
        except Error as e:
            print(f"Error al limpiar carrito DB: {e}")
        finally:
            if db.is_connected():
                cursor.close()
                db.close()