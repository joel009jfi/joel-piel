from flask import render_template, request, redirect, session, url_for
from db import conectar, obtener_cursor


def register_routes(app):
    @app.route("/mis-pedidos")
    def mis_pedidos():
        if "usuario" not in session or not session.get("Id_usuario"):
            return redirect(url_for('login'))
        usuario = session.get("usuario")
        rol = session.get("rol")
        Id_usuario = session["Id_usuario"]
        db = conectar()
        pedidos = []
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            cursor.execute("""
                SELECT p.Id_pedido, p.total, p.estado, p.fecha,
                       e.estado_envio, e.transportadora, e.numero_guia
                FROM pedidos p
                LEFT JOIN envios e ON p.Id_pedido = e.Id_pedido
                WHERE p.Id_usuario = %s
                ORDER BY p.fecha DESC
            """, (Id_usuario,))
            pedidos = cursor.fetchall()
            for pedido in pedidos:
                cursor.execute("""
                    SELECT dp.cantidad, dp.precio_unitario, pr.nombre, pr.imagen_url, pr.Id_producto
                    FROM detalle_pedido dp
                    JOIN productos pr ON dp.Id_producto = pr.Id_producto
                    WHERE dp.Id_pedido = %s
                """, (pedido['Id_pedido'],))
                pedido['productos'] = cursor.fetchall()
            db.close()
        return render_template("mis_pedidos.html", usuario=usuario, rol=rol, pedidos=pedidos)

    @app.route("/cancelar-pedido/<int:id_pedido>", methods=["POST"])
    def cancelar_pedido_cliente(id_pedido):
        if "usuario" not in session or not session.get("Id_usuario"):
            return redirect(url_for('login'))
        Id_usuario = session["Id_usuario"]
        db = conectar()
        if db:
            cursor = db.cursor()
            cursor.execute("SELECT estado FROM pedidos WHERE Id_pedido = %s AND Id_usuario = %s", (id_pedido, Id_usuario))
            pedido = cursor.fetchone()
            if pedido and pedido[0] in ("Pendiente",):
                cursor.execute("UPDATE pedidos SET estado = 'Cancelado' WHERE Id_pedido = %s", (id_pedido,))
                db.commit()
            db.close()
        return redirect(url_for('mis_pedidos'))
