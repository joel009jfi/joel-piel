from flask import render_template, request, redirect, session, url_for
from db import conectar, obtener_cursor
from services.email_service import enviar_notificacion_pago
from services.pdf_service import generar_pdf_pedido
from services.excel_service import generar_excel_pedidos
from extensions import mail


def register_routes(app):
    @app.route("/admin/ventas")
    def admin_ventas():
        """Lista de todos los pedidos con paginación (25 por página)."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        pagina = request.args.get("pagina", 1, type=int)
        por_pagina = 25
        offset = (pagina - 1) * por_pagina
        cursor.execute("SELECT COUNT(*) as total FROM pedidos")
        total_pedidos = cursor.fetchone()["total"]
        total_paginas = (total_pedidos + por_pagina - 1) // por_pagina
        # Obtiene pedidos con datos del cliente
        cursor.execute("""
            SELECT p.Id_pedido, p.Id_usuario, p.total, p.estado, p.fecha, p.metodo_pago,
                   u.nombre as cliente, u.email
            FROM pedidos p
            LEFT JOIN usuarios u ON p.Id_usuario = u.Id_usuario
            ORDER BY p.fecha DESC
            LIMIT %s OFFSET %s
        """, (por_pagina, offset))
        pedidos_db = cursor.fetchall()
        # Para cada pedido, obtiene los productos del detalle
        for pedido in pedidos_db:
            cursor.execute("""
                SELECT dp.cantidad, dp.precio_unitario, pr.nombre, pr.imagen_url
                FROM detalle_pedido dp
                JOIN productos pr ON dp.Id_producto = pr.Id_producto
                WHERE dp.Id_pedido = %s
            """, (pedido['Id_pedido'],))
            pedido['productos'] = cursor.fetchall()
        db.close()
        return render_template("ventas_admin.html", pedidos=pedidos_db, pagina=pagina, total_paginas=total_paginas)

    @app.route("/admin/ventas/<int:id_pedido>")
    def detalle_pedido(id_pedido):
        """Detalle de un pedido específico (admin)."""
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
        # Productos incluidos en el pedido
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
        """Marca pedido como Pagado y envía notificación al cliente."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = db.cursor(dictionary=True, buffered=True)
            # Obtiene datos del cliente para el email
            cursor.execute("""
                SELECT u.nombre, u.email FROM pedidos p
                JOIN usuarios u ON p.Id_usuario = u.Id_usuario
                WHERE p.Id_pedido = %s
            """, (id_pedido,))
            pedido = cursor.fetchone()
            if pedido:
                cursor.execute("UPDATE pedidos SET estado = 'Pagado' WHERE Id_pedido = %s", (id_pedido,))
                db.commit()
                try:
                    enviar_notificacion_pago(mail, pedido['nombre'], pedido['email'], id_pedido)
                except Exception as e:
                    print(f"Error al enviar notificación de pago: {e}")
            db.close()
        return redirect(url_for('admin_ventas'))

    @app.route("/admin/ventas/pdf/<int:id_pedido>")
    def descargar_pdf_pedido(id_pedido):
        """Genera y descarga el PDF de un pedido."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        return generar_pdf_pedido(id_pedido)

    @app.route("/admin/ventas/excel")
    def descargar_excel_ventas():
        """Genera y descarga el Excel de todos los pedidos."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        return generar_excel_pedidos()
