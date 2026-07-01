from flask import (
    render_template, request, redirect, session, url_for, flash
)
from db import conectar, obtener_cursor
from services.email_service import enviar_notificacion_pago, enviar_cancelacion_reembolso
from services.pdf_service import generar_pdf_pedido
from services.excel_service import generar_excel_pedidos
from extensions import mail



def register_routes(app):
    @app.route("/admin/ventas")
    def admin_ventas():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        pagina = request.args.get("pagina", 1, type=int)
        por_pagina = 25
        offset = (pagina - 1) * por_pagina
        # Filtro por rango de fechas
        fecha_desde = request.args.get("fecha_desde", "")
        fecha_hasta = request.args.get("fecha_hasta", "")
        filtro_fecha = ""
        params = []
        if fecha_desde:
            filtro_fecha += " AND p.fecha >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            filtro_fecha += " AND p.fecha <= %s"
            params.append(fecha_hasta + " 23:59:59")

        cursor.execute("SELECT COUNT(*) as total FROM pedidos WHERE archivado = 0 AND estado != 'Cancelado'" + filtro_fecha, params)
        total_pedidos = cursor.fetchone()["total"]
        total_paginas = (total_pedidos + por_pagina - 1) // por_pagina
        cursor.execute("""
            SELECT p.Id_pedido, p.Id_usuario, p.total, p.estado, p.fecha, p.metodo_pago,
                   u.nombre as cliente, u.email,
                   e.estado_envio, e.transportadora, e.numero_guia,
                   pg.estado_pago, pg.metodo_pago as pago_metodo, pg.fecha_pago
            FROM pedidos p
            LEFT JOIN usuarios u ON p.Id_usuario = u.Id_usuario
            LEFT JOIN envios e ON p.Id_pedido = e.Id_pedido
            LEFT JOIN pagos pg ON p.Id_pedido = pg.id_pedido
            WHERE p.archivado = 0 AND p.estado != 'Cancelado'""" + filtro_fecha + """
            ORDER BY p.fecha DESC
            LIMIT %s OFFSET %s
        """, params + [por_pagina, offset])
        pedidos_db = cursor.fetchall()
        for pedido in pedidos_db:
            cursor.execute("""
                SELECT dp.cantidad, dp.precio_unitario, pr.nombre, pr.imagen_url
                FROM detalle_pedido dp
                JOIN productos pr ON dp.Id_producto = pr.Id_producto
                WHERE dp.Id_pedido = %s
            """, (pedido['Id_pedido'],))
            pedido['productos'] = cursor.fetchall()
        db.close()
        agrupados = {}
        for pedido in pedidos_db:
            mp = pedido['metodo_pago'] or 'Contra entrega'
            if mp not in agrupados:
                agrupados[mp] = []
            agrupados[mp].append(pedido)
        return render_template("ventas_admin.html", agrupados=agrupados, pedidos=pedidos_db, pagina=pagina, total_paginas=total_paginas)

    @app.route("/admin/ventas/<int:id_pedido>")
    def detalle_pedido(id_pedido):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        # JOIN completo con usuario y envío
        cursor.execute("""
            SELECT p.Id_pedido, p.total, p.estado, p.fecha, p.metodo_pago,
                   u.nombre, u.email, e.direccion_envio, e.estado_envio,
                   e.transportadora, e.numero_guia
            FROM pedidos p
            JOIN usuarios u ON p.Id_usuario = u.Id_usuario
            LEFT JOIN envios e ON p.Id_pedido = e.Id_pedido
            WHERE p.Id_pedido = %s
        """, (id_pedido,))
        pedido = cursor.fetchone()
        if not pedido:
            db.close()
            return redirect(url_for('admin_ventas'))
        cursor.execute("""
            SELECT dp.cantidad, dp.precio_unitario, pr.nombre, pr.imagen_url
            FROM detalle_pedido dp
            JOIN productos pr ON dp.Id_producto = pr.Id_producto
            WHERE dp.Id_pedido = %s
        """, (id_pedido,))
        pedido['productos'] = cursor.fetchall()
        db.close()
        return render_template("detalle_pedido.html", pedido=pedido)

    @app.route("/admin/ventas/confirmar-pago/<int:id_pedido>", methods=["POST"])
    def confirmar_pago(id_pedido):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = db.cursor(dictionary=True, buffered=True)
            cursor.execute("""
                SELECT u.nombre, u.email, p.estado, p.metodo_pago, pg.estado_pago FROM pedidos p
                JOIN usuarios u ON p.Id_usuario = u.Id_usuario
                LEFT JOIN pagos pg ON p.Id_pedido = pg.id_pedido
                WHERE p.Id_pedido = %s
            """, (id_pedido,))
            pedido = cursor.fetchone()
            if pedido and pedido['metodo_pago'] == 'Contra entrega' and pedido['estado_pago'] != 'Aprobado':
                cursor.execute("UPDATE pagos SET estado_pago='Aprobado', fecha_pago=NOW() WHERE id_pedido=%s", (id_pedido,))
                cursor.execute("SELECT estado_envio FROM envios WHERE Id_pedido=%s", (id_pedido,))
                envio_actual = cursor.fetchone()
                if envio_actual and envio_actual['estado_envio'] != 'Entregado':
                    cursor.execute("UPDATE pedidos SET estado = 'Entregado' WHERE Id_pedido = %s", (id_pedido,))
                    cursor.execute("UPDATE envios SET estado_envio = 'Entregado' WHERE Id_pedido = %s", (id_pedido,))
                db.commit()
            db.close()
        return redirect(url_for('admin_ventas'))

    @app.route("/admin/pedidos/cancelar/<int:id_pedido>", methods=["POST"])
    def admin_cancelar_pedido(id_pedido):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = db.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT estado, metodo_pago, Id_usuario FROM pedidos WHERE Id_pedido = %s", (id_pedido,))
        pedido = cursor.fetchone()
        cursor.execute("SELECT estado_envio FROM envios WHERE Id_pedido = %s", (id_pedido,))
        envio = cursor.fetchone()
        if pedido and pedido['estado'] in ("Pendiente",) and (not envio or envio['estado_envio'] != 'Entregado'):
            cursor.execute("SELECT Id_producto, cantidad FROM detalle_pedido WHERE Id_pedido = %s", (id_pedido,))
            for prod in cursor.fetchall():
                cursor.execute("UPDATE productos SET stock = stock + %s WHERE id_producto = %s", (prod['cantidad'], prod['Id_producto']))
            cursor.execute("DELETE FROM envios WHERE Id_pedido = %s", (id_pedido,))
            cursor.execute("DELETE FROM pagos WHERE id_pedido = %s", (id_pedido,))
            cursor.execute("DELETE FROM detalle_pedido WHERE Id_pedido = %s", (id_pedido,))
            cursor.execute("DELETE FROM pedidos WHERE Id_pedido = %s", (id_pedido,))
            db.commit()
            if pedido['metodo_pago'] == 'En l\u00ednea':
                cursor.execute("SELECT email FROM usuarios WHERE Id_usuario = %s", (pedido['Id_usuario'],))
                row = cursor.fetchone()
                email = row['email'] if row else None
                if email:
                    enviar_cancelacion_reembolso(mail, "Admin", email, id_pedido)
            flash("Pedido cancelado correctamente.", "success")
        else:
            flash("Este pedido no se puede cancelar.", "danger")
        db.close()
        return redirect(url_for('admin_ventas'))

    @app.route("/admin/ventas/finalizar-mes", methods=["POST"])
    def finalizar_mes():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        from services.excel_service import exportar_ventas_excel
        db = conectar()
        if not db:
            return "Error de conexión", 500
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("""
            SELECT p.Id_pedido, p.total, p.estado, p.fecha, p.metodo_pago,
                   u.nombre as cliente, u.email
            FROM pedidos p
            LEFT JOIN usuarios u ON p.Id_usuario = u.Id_usuario
            ORDER BY p.fecha ASC
        """)
        ventas = cursor.fetchall()
        productos_por_pedido = {}
        for v in ventas:
            cursor.execute("""
                SELECT dp.cantidad, dp.precio_unitario, pr.nombre
                FROM detalle_pedido dp
                JOIN productos pr ON dp.Id_producto = pr.Id_producto
                WHERE dp.Id_pedido = %s
            """, (v["Id_pedido"],))
            productos_por_pedido[v["Id_pedido"]] = [
                {**p, "subtotal": p["cantidad"] * p["precio_unitario"]} for p in cursor.fetchall()
            ]
        if ventas:
            response = exportar_ventas_excel(ventas, productos_por_pedido)
            cursor.execute("UPDATE pedidos SET archivado = 1")
            db.commit()
        db.close()
        return response if ventas else redirect(url_for('admin_ventas'))

    @app.route("/admin/ventas/pdf/<int:id_pedido>")
    def descargar_pdf_pedido(id_pedido):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        return generar_pdf_pedido(id_pedido)

    @app.route("/admin/ventas/excel")
    def descargar_excel_ventas():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        return generar_excel_pedidos()
