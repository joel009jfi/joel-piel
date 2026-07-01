from flask import render_template, redirect, session, url_for
from db import conectar, obtener_cursor


def register_routes(app):
    @app.route("/admin")
    def admin_panel():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return render_template("admin.html", pedidos=[], total_ventas=0, en_camino=0, entregados=0, por_despachar=0, stock_bajo=[], mensajes_no_leidos=0)
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("""
            SELECT p.Id_pedido, p.Id_usuario, p.total, COALESCE(e.estado_envio, p.estado) as estado, p.fecha, u.nombre as cliente, u.email
            FROM pedidos p
            LEFT JOIN usuarios u ON p.Id_usuario = u.Id_usuario
            LEFT JOIN envios e ON p.Id_pedido = e.Id_pedido
            WHERE (p.archivado = 0 OR p.archivado IS NULL)
            ORDER BY p.fecha DESC LIMIT 5
        """)
        pedidos_db = cursor.fetchall()
        # Suma total de ventas (solo pedidos con pago aprobado, excluye pendientes y cancelados)
        cursor.execute("""
            SELECT SUM(p.total) as gran_total FROM pedidos p
            LEFT JOIN pagos pg ON p.Id_pedido = pg.id_pedido
            WHERE p.estado NOT IN ('Cancelado', 'Pendiente')
            AND (p.metodo_pago = 'En l\u00ednea' OR pg.estado_pago = 'Aprobado')
            AND (p.archivado = 0 OR p.archivado IS NULL)
        """)
        res_ventas = cursor.fetchone()
        total_ventas = res_ventas['gran_total'] if res_ventas and res_ventas['gran_total'] else 0
        cursor.execute("""
            SELECT COUNT(*) as en_camino FROM envios e
            JOIN pedidos p ON e.Id_pedido = p.Id_pedido
            WHERE e.estado_envio = 'Enviado' AND (p.archivado = 0 OR p.archivado IS NULL)
        """)
        res_camino = cursor.fetchone()
        en_camino = res_camino['en_camino'] if res_camino else 0
        cursor.execute("""
            SELECT COUNT(*) as entregados FROM envios e
            JOIN pedidos p ON e.Id_pedido = p.Id_pedido
            WHERE e.estado_envio = 'Entregado' AND (p.archivado = 0 OR p.archivado IS NULL)
        """)
        res_entregados = cursor.fetchone()
        entregados = res_entregados['entregados'] if res_entregados else 0
        cursor.execute("""
            SELECT COUNT(*) as pd FROM envios e
            JOIN pedidos p ON e.Id_pedido = p.Id_pedido
            WHERE (e.estado_envio IN ('Por despachar', 'Preparando') OR e.estado_envio IS NULL)
            AND (p.archivado = 0 OR p.archivado IS NULL)
        """)
        res_pd = cursor.fetchone()
        por_despachar = res_pd['pd'] if res_pd else 0
        # Productos con stock <= 3 (alerta de inventario bajo)
        cursor.execute("SELECT id_producto, nombre, stock FROM productos WHERE stock <= 3 ORDER BY stock ASC LIMIT 5")
        stock_bajo = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) as total FROM contactos WHERE leido = 0")
        res_mensajes = cursor.fetchone()
        mensajes_no_leidos = res_mensajes['total'] if res_mensajes else 0
        db.close()
        return render_template("admin.html", pedidos=pedidos_db, total_ventas=total_ventas, en_camino=en_camino, entregados=entregados, por_despachar=por_despachar, stock_bajo=stock_bajo, mensajes_no_leidos=mensajes_no_leidos)

