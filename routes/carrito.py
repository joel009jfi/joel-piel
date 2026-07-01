from flask import render_template, session, jsonify
from db import conectar, obtener_cursor
from extensions import csrf
from services.helpers import datos_carrito, sincronizar_carrito_db


def register_routes(app):
    @app.route("/carrito")
    def ver_carrito():
        productos, total, _ = datos_carrito()
        return render_template("carrito.html", productos=productos, total=total)

    @app.route("/carrito/agregar/<int:id_producto>", methods=["POST"])
    @csrf.exempt
    def agregar_al_carrito(id_producto):
        db = conectar()
        if not db:
            return jsonify({"status": "error", "message": "Error de conexión"}), 500
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT stock FROM productos WHERE id_producto = %s", (id_producto,))
        prod = cursor.fetchone()
        db.close()
        if not prod:
            return jsonify({"status": "error", "message": "El producto no existe"}), 404
        if prod['stock'] < 1:
            return jsonify({"status": "error", "message": "Producto agotado"}), 400

        if "carrito" not in session:
            session["carrito"] = {}
        carrito = session["carrito"]
        id_str = str(id_producto)
        cantidad_actual = carrito.get(id_str, 0)
        if cantidad_actual + 1 > prod['stock']:
            return jsonify({
                "status": "error",
                "message": f"Solo hay {prod['stock']} unidades disponibles"
            }), 400
        if id_str in carrito:
            carrito[id_str] += 1
        else:
            carrito[id_str] = 1
        session["carrito"] = carrito
        sincronizar_carrito_db()
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
        carrito = session.get("carrito", {})
        id_str = str(id_producto)
        producto_removido = False
        nueva_cantidad = 0
        nuevo_subtotal = 0
        if id_str in carrito:
            carrito[id_str] -= 1
            nueva_cantidad = carrito[id_str]
            if carrito[id_str] <= 0:
                del carrito[id_str]
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
