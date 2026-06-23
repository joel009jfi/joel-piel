from flask import render_template, redirect, session, url_for
from db import conectar, obtener_cursor


def register_routes(app):
    @app.route("/admin")
    def admin_panel():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return render_template("admin.html", pedidos=[], total_ventas=0, pendientes=0, en_camino=0, entregados=0)
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("""
            SELECT p.Id_pedido, p.Id_usuario, p.total, p.estado, p.fecha, u.nombre as cliente, u.email
            FROM pedidos p
            LEFT JOIN usuarios u ON p.Id_usuario = u.Id_usuario
            ORDER BY p.fecha DESC LIMIT 5
        """)
        pedidos_db = cursor.fetchall()
        # Suma total de ventas (excluye cancelados)
        cursor.execute("SELECT SUM(total) as gran_total FROM pedidos WHERE estado != 'Cancelado'")
        res_ventas = cursor.fetchone()
        total_ventas = res_ventas['gran_total'] if res_ventas and res_ventas['gran_total'] else 0
        cursor.execute("SELECT COUNT(*) as pendientes FROM pedidos WHERE estado = 'Pendiente'")
        res_pendientes = cursor.fetchone()
        conteo_pendientes = res_pendientes['pendientes'] if res_pendientes else 0
        cursor.execute("SELECT COUNT(*) as en_camino FROM pedidos WHERE estado = 'Enviado'")
        res_camino = cursor.fetchone()
        en_camino = res_camino['en_camino'] if res_camino else 0
        cursor.execute("SELECT COUNT(*) as entregados FROM envios WHERE estado_envio = 'Entregado'")
        res_entregados = cursor.fetchone()
        entregados = res_entregados['entregados'] if res_entregados else 0
        # Productos con stock <= 3 (alerta de inventario bajo)
        cursor.execute("SELECT id_producto, nombre, stock FROM productos WHERE stock <= 3 ORDER BY stock ASC LIMIT 5")
        stock_bajo = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) as total FROM contactos WHERE leido = 0")
        res_mensajes = cursor.fetchone()
        mensajes_no_leidos = res_mensajes['total'] if res_mensajes else 0
        db.close()
        return render_template("admin.html", pedidos=pedidos_db, total_ventas=total_ventas, pendientes=conteo_pendientes, en_camino=en_camino, entregados=entregados, stock_bajo=stock_bajo, mensajes_no_leidos=mensajes_no_leidos)

    @app.route("/actualizar_estado/<int:id_pedido>/<nuevo_estado>")
    def actualizar_estado(id_pedido, nuevo_estado):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        cursor = obtener_cursor(db)
        cursor.execute("UPDATE pedidos SET estado = %s WHERE Id_pedido = %s", (nuevo_estado, id_pedido))
        db.commit()
        db.close()
        return redirect(url_for('admin_panel'))
