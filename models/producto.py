from db import conectar, obtener_cursor
from mysql.connector import Error


def registrar_producto(nombre, precio, stock, imagen_url, id_categoria, descripcion=''):
    """INSERT: crea un producto en el inventario con imagen y categoría."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            sql = """INSERT INTO productos (nombre, precio, stock, imagen_url, Id_categoria, descripcion)
                     VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(sql, (nombre, precio, stock, imagen_url, id_categoria, descripcion))
            db.commit()
            return True
        except Error as e:
            print(f"Error al registrar producto: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return False


def actualizar_stock_db(id_producto, nuevo_stock):
    """UPDATE: cambia el stock de un producto a un valor específico."""
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


def descontar_stock(id_producto, cantidad):
    """UPDATE: descuenta una cantidad del stock actual de un producto."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            # Resta cantidad al stock existente en la BD
            cursor.execute("UPDATE productos SET stock = stock - %s WHERE id_producto = %s", (cantidad, id_producto))
            db.commit()
            return True
        except Error as e:
            print(f"Error al descontar stock: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return False


def obtener_productos_activos():
    """SELECT: retorna productos con stock > 0 ordenados descendente."""
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute(
            "SELECT Id_producto, nombre, precio, imagen_url, descripcion FROM productos WHERE stock > 0 ORDER BY Id_producto DESC"
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener productos activos: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_producto_por_id(id_producto):
    """SELECT: retorna un producto completo por su id, o None."""
    db = conectar()
    if not db:
        return None
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener producto: {e}")
        return None
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_stock(id_producto):
    """SELECT: retorna el stock actual de un producto (entero)."""
    db = conectar()
    if not db:
        return 0
    try:
        cursor = db.cursor()
        cursor.execute("SELECT stock FROM productos WHERE id_producto = %s", (id_producto,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else 0
    except Error as e:
        print(f"Error al obtener stock: {e}")
        return 0
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_productos_por_ids(ids):
    """SELECT: retorna varios productos por una lista de IDs."""
    if not ids:
        return []
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        # Genera placeholders dinámicos (ej: %s,%s,%s para 3 IDs)
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(
            f"SELECT id_producto, nombre, precio, imagen_url, stock FROM productos WHERE id_producto IN ({placeholders})",
            ids
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener productos por IDs: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_todos_productos_admin():
    """SELECT: retorna todos los productos incluyendo nombre de categoría (admin)."""
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute(
            "SELECT p.*, c.nombre_categoria FROM productos p LEFT JOIN categorias c ON p.Id_categoria = c.Id_categoria ORDER BY p.Id_producto DESC"
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener productos admin: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def editar_producto_en_db(id_producto, nombre, descripcion, precio, stock, imagen_url, id_categoria):
    """UPDATE: modifica todos los campos editables de un producto."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            sql = """UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, stock=%s,
                     imagen_url=%s, Id_categoria=%s WHERE Id_producto=%s"""
            cursor.execute(sql, (nombre, descripcion, precio, stock, imagen_url, id_categoria, id_producto))
            db.commit()
            return True
        except Error as e:
            print(f"Error al editar producto: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return False


def eliminar_producto_de_db(id_producto):
    """DELETE: elimina un producto por su Id_producto."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM productos WHERE Id_producto = %s", (id_producto,))
            db.commit()
            return True
        except Error as e:
            print(f"Error al eliminar producto: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return False


def contar_productos():
    """SELECT COUNT: cantidad total de productos en inventario."""
    db = conectar()
    if not db:
        return 0
    try:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos")
        return cursor.fetchone()[0]
    except Error as e:
        print(f"Error al contar productos: {e}")
        return 0
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def contar_productos_agotados():
    """SELECT COUNT: cantidad de productos con stock = 0."""
    db = conectar()
    if not db:
        return 0
    try:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM productos WHERE stock = 0")
        return cursor.fetchone()[0]
    except Error as e:
        print(f"Error al contar productos agotados: {e}")
        return 0
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_categorias():
    """SELECT: retorna todas las categorías ordenadas por ID (para formularios)."""
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
