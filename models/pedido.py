from db import conectar, obtener_cursor
from mysql.connector import Error


def crear_pedido(id_usuario, total, direccion, ciudad, codigo_postal, carrito_items):
    """Crea un pedido y sus detalles en una transacción. Retorna el ID del pedido o None."""
    db = conectar()
    if not db:
        return None
    try:
        cursor = db.cursor()
        # Primero inserta el pedido principal
        sql_pedido = "INSERT INTO pedidos (Id_usuario, total, direccion, ciudad, codigo_postal, estado) VALUES (%s, %s, %s, %s, %s, 'pendiente')"
        cursor.execute(sql_pedido, (id_usuario, total, direccion, ciudad, codigo_postal))
        id_pedido = cursor.lastrowid  # Obtiene el ID auto-generado

        # Luego inserta cada producto del carrito en detalle_pedido
        sql_detalle = "INSERT INTO detalle_pedido (Id_pedido, Id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)"
        for item in carrito_items:
            cursor.execute(sql_detalle, (id_pedido, item['id_producto'], item['cantidad'], item['precio']))

        db.commit()
        return id_pedido
    except Error as e:
        db.rollback()  # Revierte todo si hay error (transacción atómica)
        print(f"Error al crear pedido: {e}")
        return None
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_pedidos_por_usuario(id_usuario):
    """SELECT: retorna los pedidos de un usuario ordenados por fecha descendente."""
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute(
            "SELECT Id_pedido, fecha, total, estado FROM pedidos WHERE Id_usuario = %s ORDER BY fecha DESC",
            (id_usuario,)
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener pedidos del usuario: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_pedido_por_id(id_pedido):
    """SELECT: retorna un pedido por su ID (sin verificar usuario)."""
    db = conectar()
    if not db:
        return None
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM pedidos WHERE Id_pedido = %s", (id_pedido,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener pedido: {e}")
        return None
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_pedido_si_es_del_usuario(id_pedido, id_usuario):
    """SELECT: retorna un pedido solo si pertenece al usuario indicado."""
    db = conectar()
    if not db:
        return None
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM pedidos WHERE Id_pedido = %s AND Id_usuario = %s", (id_pedido, id_usuario))
        return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener pedido del usuario: {e}")
        return None
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_detalles_pedido(id_pedido):
    """SELECT: retorna los productos (nombre, cantidad, precio) de un pedido."""
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute(
            """SELECT dp.Id_producto, p.nombre, dp.cantidad, dp.precio_unitario
               FROM detalle_pedido dp
               JOIN productos p ON dp.Id_producto = p.id_producto
               WHERE dp.Id_pedido = %s""",
            (id_pedido,)
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener detalles del pedido: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_todos_pedidos():
    """SELECT: retorna todos los pedidos con nombre del cliente, ordenados descendente."""
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute(
            """SELECT p.Id_pedido, p.fecha, p.total, p.estado, p.direccion, p.ciudad, u.nombre
               FROM pedidos p
               JOIN usuarios u ON p.Id_usuario = u.Id_usuario
               ORDER BY p.fecha DESC"""
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener todos los pedidos: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_pedidos_logistica():
    """SELECT: retorna pedidos con datos completos para la vista de logística."""
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute(
            "SELECT Id_pedido, fecha, total, direccion, ciudad, codigo_postal, estado, Id_usuario FROM pedidos ORDER BY fecha DESC"
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener pedidos logística: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def actualizar_estado_pedido(id_pedido, nuevo_estado):
    """UPDATE: cambia el estado de un pedido (Pendiente/Pagado/Cancelado)."""
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("UPDATE pedidos SET estado = %s WHERE Id_pedido = %s", (nuevo_estado, id_pedido))
            db.commit()
            return True
        except Error as e:
            print(f"Error al actualizar estado del pedido: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return False


def contar_pedidos():
    """SELECT COUNT: cantidad total de pedidos."""
    db = conectar()
    if not db:
        return 0
    try:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        return cursor.fetchone()[0]
    except Error as e:
        print(f"Error al contar pedidos: {e}")
        return 0
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def contar_pedidos_pendientes():
    """SELECT COUNT: cantidad de pedidos con estado 'pendiente'."""
    db = conectar()
    if not db:
        return 0
    try:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM pedidos WHERE estado = 'pendiente'")
        return cursor.fetchone()[0]
    except Error as e:
        print(f"Error al contar pedidos pendientes: {e}")
        return 0
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_ventas_del_mes():
    """SELECT SUM: retorna el total de ventas del mes actual."""
    db = conectar()
    if not db:
        return 0
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(total), 0) FROM pedidos WHERE YEAR(fecha) = YEAR(CURDATE()) AND MONTH(fecha) = MONTH(CURDATE())"
        )
        return cursor.fetchone()[0]
    except Error as e:
        print(f"Error al obtener ventas del mes: {e}")
        return 0
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_ultimos_pedidos(limite=5):
    """SELECT: retorna los últimos N pedidos con nombre del cliente."""
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute(
            """SELECT p.Id_pedido, p.fecha, p.total, p.estado, u.nombre
               FROM pedidos p
               JOIN usuarios u ON p.Id_usuario = u.Id_usuario
               ORDER BY p.fecha DESC LIMIT %s""",
            (limite,)
        )
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener últimos pedidos: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()
