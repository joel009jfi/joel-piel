from db import conectar, obtener_cursor
from mysql.connector import Error


def guardar_mensaje(nombre, email, asunto, mensaje):
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            sql = "INSERT INTO contactos (nombre, email, asunto, mensaje) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nombre, email, asunto, mensaje))
            db.commit()
            return True
        except Error as e:
            print(f"Error al guardar mensaje: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return False


def obtener_mensajes():
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM contactos ORDER BY fecha DESC")
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener mensajes: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def contar_mensajes_no_leidos():
    db = conectar()
    if not db:
        return 0
    try:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM contactos WHERE leido = 0")
        return cursor.fetchone()[0]
    except Error as e:
        print(f"Error al contar mensajes no leídos: {e}")
        return 0
    finally:
        if db.is_connected():
            cursor.close()
            db.close()
