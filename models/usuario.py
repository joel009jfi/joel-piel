from db import conectar, obtener_cursor
from mysql.connector import Error


def registrar_usuario(nombre, email, password_hash, rol='cliente'):
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            sql = "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nombre, email, password_hash, rol))
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


def obtener_usuario_por_email(email):
    db = conectar()
    if not db:
        return None
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener usuario por email: {e}")
        return None
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_usuario_por_id(id_usuario):
    db = conectar()
    if not db:
        return None
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM usuarios WHERE Id_usuario = %s", (id_usuario,))
        return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener usuario por ID: {e}")
        return None
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def obtener_todos_usuarios():
    db = conectar()
    if not db:
        return []
    try:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT Id_usuario, nombre, email, rol FROM usuarios ORDER BY Id_usuario DESC")
        return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener usuarios: {e}")
        return []
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def contar_clientes():
    db = conectar()
    if not db:
        return 0
    try:
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE rol = 'cliente'")
        return cursor.fetchone()[0]
    except Error as e:
        print(f"Error al contar clientes: {e}")
        return 0
    finally:
        if db.is_connected():
            cursor.close()
            db.close()


def eliminar_usuario_db(id_usuario):
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM usuarios WHERE Id_usuario = %s", (id_usuario,))
            db.commit()
            return True
        except Error as e:
            print(f"Error al eliminar usuario: {e}")
            return False
        finally:
            if db.is_connected():
                cursor.close()
                db.close()
    return False
