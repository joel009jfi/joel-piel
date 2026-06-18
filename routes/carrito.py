from flask import render_template, session, jsonify  # jsonify para respuestas AJAX
from extensions import csrf
from services.helpers import datos_carrito, sincronizar_carrito_db


def register_routes(app):
    @app.route("/carrito")
    def ver_carrito():
        """Página completa del carrito de compras."""
        productos, total, _ = datos_carrito()
        return render_template("carrito.html", productos=productos, total=total)

    @app.route("/carrito/agregar/<int:id_producto>", methods=["POST"])
    @csrf.exempt  # Desactiva CSRF para peticiones AJAX del carrito
    def agregar_al_carrito(id_producto):
        """AJAX: agrega 1 unidad al carrito desde detalle o grid. Retorna JSON."""
        if "carrito" not in session:
            session["carrito"] = {}
        carrito = session["carrito"]
        id_str = str(id_producto)  # Las claves del carrito son strings
        if id_str in carrito:
            carrito[id_str] += 1  # Incrementa cantidad si ya existe
        else:
            carrito[id_str] = 1   # Agrega producto nuevo
        session["carrito"] = carrito
        sincronizar_carrito_db()  # Guarda en BD si el usuario está logueado
        # Recalcula datos para la respuesta JSON
        productos_carrito, total_carrito, cantidad_total_carrito = datos_carrito()
        nuevo_subtotal = 0
        for p in productos_carrito:
            if str(p['id_producto']) == id_str:
                nuevo_subtotal = p['subtotal']
                break
        return jsonify({
            "status": "success",
            "message": "Bolso agregado con éxito",
            "nueva_cantidad": carrito[id_str],
            "nuevo_subtotal": nuevo_subtotal,
            "total_carrito": total_carrito,
            "cantidad_total_carrito": cantidad_total_carrito,
            "producto_removido": False
        })

    @app.route("/carrito/restar/<int:id_producto>", methods=["POST"])
    @csrf.exempt
    def restar_del_carrito(id_producto):
        """AJAX: resta 1 unidad. Si llega a 0, remueve el item. Retorna JSON."""
        carrito = session.get("carrito", {})
        id_str = str(id_producto)
        producto_removido = False
        nueva_cantidad = 0
        nuevo_subtotal = 0
        if id_str in carrito:
            carrito[id_str] -= 1
            nueva_cantidad = carrito[id_str]
            if carrito[id_str] <= 0:
                del carrito[id_str]  # Elimina del carrito si queda en 0
                producto_removido = True
            session["carrito"] = carrito
            sincronizar_carrito_db()
        productos_carrito, total_carrito, cantidad_total_carrito = datos_carrito()
        if not producto_removido:
            for p in productos_carrito:
                if str(p['id_producto']) == id_str:
                    nuevo_subtotal = p['subtotal']
                    break
        return jsonify({
            "status": "success",
            "nueva_cantidad": nueva_cantidad,
            "nuevo_subtotal": nuevo_subtotal,
            "total_carrito": total_carrito,
            "cantidad_total_carrito": cantidad_total_carrito,
            "producto_removido": producto_removido
        })

    @app.route("/carrito/eliminar/<int:id_producto>", methods=["POST"])
    @csrf.exempt
    def eliminar_del_carrito(id_producto):
        """AJAX: elimina un producto completamente del carrito. Retorna JSON."""
        carrito = session.get("carrito", {})
        id_str = str(id_producto)
        producto_removido = False
        if id_str in carrito:
            del carrito[id_str]
            session["carrito"] = carrito
            sincronizar_carrito_db()
            producto_removido = True
        productos_carrito, total_carrito, cantidad_total_carrito = datos_carrito()
        return jsonify({
            "status": "success",
            "producto_removido": producto_removido,
            "total_carrito": total_carrito,
            "cantidad_total_carrito": cantidad_total_carrito
        })
