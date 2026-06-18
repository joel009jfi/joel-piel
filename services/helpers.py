from flask import session
from db import conectar, obtener_cursor

# Constantes globales
MESES_ES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
COSTO_ENVIO = 15000  # $15.000/kg — se paga a la transportadora al recibir


def datos_carrito():
    """Consulta BD para obtener productos, total y cantidad del carrito actual en sesión."""
    carrito = session.get("carrito", {})  # Dict {id_producto: cantidad}
    productos = []
    total = 0
    cantidad_total = 0
    db = conectar()
    if db:
        if carrito:
            cursor = obtener_cursor(db, diccionario=True)
            # Itera sobre cada producto en el carrito de la sesión
            for id_producto, cantidad in carrito.items():
                cursor.execute("SELECT id_producto, nombre, precio, imagen_url, stock FROM productos WHERE id_producto = %s", (id_producto,))
                producto = cursor.fetchone()
                if producto:
                    producto['cantidad'] = cantidad
                    # Calcula subtotal por producto
                    precio = float(producto['precio']) if producto['precio'] is not None else 0
                    subtotal = precio * cantidad
                    producto['subtotal'] = subtotal
                    total += subtotal
                    cantidad_total += cantidad
                    productos.append(producto)
        db.close()
    return productos, total, cantidad_total


def sincronizar_carrito_db():
    """Guarda el carrito de la sesión en BD cuando hay un usuario logueado."""
    Id_usuario = session.get("Id_usuario")
    if Id_usuario:
        carrito = session.get("carrito", {})
        from models.carrito import guardar_carrito_db  # Import local evita ciclo
        guardar_carrito_db(Id_usuario, carrito)


def allowed_file(filename):
    """Verifica que la extensión del archivo subido esté permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif'}


def stock_valido(valor):
    """Valida que el valor de stock sea un entero >= 0."""
    try:
        n = int(valor)
        return n >= 0
    except (ValueError, TypeError):
        return False
