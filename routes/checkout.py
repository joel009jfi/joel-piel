from flask import render_template, request, redirect, session, url_for
from db import conectar, obtener_cursor
from models.carrito import limpiar_carrito_db
from services.email_service import enviar_confirmacion_compra
from services.helpers import datos_carrito, COSTO_ENVIO
from extensions import mail


def register_routes(app):
    @app.route("/carrito/checkout")
    def checkout():
        if "usuario" not in session:
            return redirect(url_for('login'))
        carrito = session.get("carrito", {})
        if not carrito:
            return redirect(url_for('inicio'))
        productos, total, cantidad = datos_carrito()
        return render_template("checkout.html", productos=productos, total=total, cantidad_total=cantidad, costo_envio=COSTO_ENVIO)

    @app.route("/carrito/finalizar", methods=["POST"])
    def finalizar_compra():
        if "usuario" not in session:
            return redirect(url_for('login'))
        carrito = session.get("carrito", {})
        if not carrito:
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = db.cursor(dictionary=True, buffered=True)
            cursor.execute("SELECT Id_usuario, email FROM usuarios WHERE nombre = %s", (session["usuario"],))
            usuario_db = cursor.fetchone()
            if not usuario_db:
                cursor.close()
                db.close()
                return "Error: Usuario no encontrado", 404
            id_usuario = usuario_db["Id_usuario"]
            email_usuario = usuario_db["email"]
            departamento = request.form.get("departamento", "Por definir")
            ciudad = request.form.get("ciudad", "Por definir")
            direccion_cruda = request.form.get("direccion", "Por definir")
            telefono = request.form.get("telefono", "")
            metodo_pago = request.form.get("metodo_pago", "Contraentrega")
            direccion_completa = f"{direccion_cruda}, {ciudad} - {departamento}. Tel: {telefono}"
            total = 0
            items_a_procesar = []
            for id_producto, cantidad in carrito.items():
                cursor.execute("SELECT id_producto, precio, stock FROM productos WHERE id_producto = %s", (id_producto,))
                prod = cursor.fetchone()
                if prod:
                    if prod['stock'] < cantidad:
                        cursor.close()
                        db.close()
                        return "Lo sentimos, stock insuficiente para procesar la compra.", 400
                    total += float(prod['precio']) * cantidad
                    items_a_procesar.append({
                        'id': id_producto,
                        'nuevo_stock': prod['stock'] - cantidad
                    })
            try:
                estado_inicial = "Pagado" if metodo_pago == "Completo" else "Pendiente"
                cursor.execute(
                    "INSERT INTO pedidos (Id_usuario, total, estado, metodo_pago, fecha) VALUES (%s, %s, %s, %s, NOW())",
                    (id_usuario, total, estado_inicial, metodo_pago)
                )
                id_pedido_nuevo = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO envios (Id_pedido, direccion_envio, estado_envio, numero_guia, transportadora) VALUES (%s, %s, 'Por despachar', 'Contraentrega', 'Por asignar')",
                    (id_pedido_nuevo, direccion_completa)
                )
                for item in items_a_procesar:
                    cursor.execute("UPDATE productos SET stock = %s WHERE id_producto = %s", (item['nuevo_stock'], item['id']))
                db.commit()
                session.pop("carrito", None)
                if session.get("Id_usuario"):
                    limpiar_carrito_db(session["Id_usuario"])
                try:
                    enviar_confirmacion_compra(mail, session["usuario"], email_usuario, id_pedido_nuevo, metodo_pago)
                except Exception as e:
                    print(f"Error al enviar confirmación de compra: {e}")
                return render_template("compra_exitosa.html", pedido_id=id_pedido_nuevo)
            except Exception as e:
                db.rollback()
                print(f"Error en la transacción de compra: {e}")
                return "Error interno al procesar la transacción", 500
            finally:
                cursor.close()
                db.close()
        return "Error de conexión con la base de datos", 500
