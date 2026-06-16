from db import conectar, obtener_cursor
from mysql.connector import Error


def guardar_carrito_db(id_usuario, carrito_dict):
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM carrito WHERE Id_usuario = %s", (id_usuario,))
            for id_producto, cantidad in carrito_dict.items():
                cursor.execute(
                    "INSERT INTO carrito (Id_usuario, id_producto, cantidad) VALUES (%s, %s, %s)",
                    (id_usuario, int(id_producto), cantidad)
                )
            db.commit()
        except Error as e:
            print(f"Error al guardar carrito en DB: {e}")
        finally:
            if db.is_connected():
                cursor.close()
                db.close()


def cargar_carrito_db(id_usuario):
    db = conectar()
    if db:
        try:
            cursor = obtener_cursor(db, diccionario=True)
            cursor.execute("SELECT id_producto, cantidad FROM carrito WHERE Id_usuario = %s", (id_usuario,))
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


def limpiar_carrito_db(id_usuario):
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM carrito WHERE Id_usuario = %s", (id_usuario,))
            db.commit()
        except Error as e:
            print(f"Error al limpiar carrito DB: {e}")
        finally:
            if db.is_connected():
                cursor.close()
                db.close()


def asegurar_tabla_carrito():
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
