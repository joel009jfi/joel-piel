from flask import (
    render_template, request, redirect, session, url_for
)
from db import conectar, obtener_cursor
from services.email_service import enviar_agradecimiento_entrega, enviar_notificacion_despacho
from extensions import mail


def register_routes(app):
    @app.route("/admin/envios")
    def admin_envios():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        # JOIN de envios, pedidos y usuarios para vista completa
        cursor.execute("""
            SELECT e.Id_envios, e.Id_pedido, e.direccion_envio, e.estado_envio,
                   e.numero_guia, e.transportadora, p.total, p.estado as estado_pago,
                   p.metodo_pago, p.fecha, u.nombre as cliente
            FROM envios e
            JOIN pedidos p ON e.Id_pedido = p.Id_pedido
            JOIN usuarios u ON p.Id_usuario = u.Id_usuario
            ORDER BY e.Id_envios DESC
        """)
        envios = cursor.fetchall()
        db.close()
        pendientes = [e for e in envios if e['estado_envio'] != 'Entregado']
        entregados = [e for e in envios if e['estado_envio'] == 'Entregado']
        return render_template("logistica_admin.html", pendientes=pendientes, entregados=entregados)

    @app.route("/admin/envios/reabrir/<int:id_envio>", methods=["POST"])
    def reabrir_envio(id_envio):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db)
            cursor.execute("UPDATE envios SET estado_envio='Por despachar' WHERE Id_envios=%s AND estado_envio='Entregado'", (id_envio,))
            if cursor.rowcount:
                cursor.execute("SELECT Id_pedido FROM envios WHERE Id_envios=%s", (id_envio,))
                row = cursor.fetchone()
                if row:
                    cursor.execute("UPDATE pedidos SET estado='Pendiente' WHERE Id_pedido=%s", (row['Id_pedido'],))
            db.commit()
            db.close()
        return redirect(url_for('admin_envios'))

    @app.route("/admin/envios/agradecer/<int:id_envio>", methods=["POST"])
    def agradecer_envio(id_envio):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            cursor.execute("""
                SELECT u.nombre, u.email, e.Id_pedido FROM usuarios u
                JOIN pedidos p ON u.Id_usuario = p.Id_usuario
                JOIN envios e ON e.Id_pedido = p.Id_pedido
                WHERE e.Id_envios = %s AND e.estado_envio = 'Entregado'
            """, (id_envio,))
            datos = cursor.fetchone()
            db.close()
            if datos:
                try:
                    enviar_agradecimiento_entrega(mail, datos['nombre'], datos['email'], datos['Id_pedido'])
                except Exception as e:
                    print(f"Error al enviar agradecimiento: {e}")
        return redirect(url_for('admin_envios'))

    @app.route("/admin/envios/actualizar/<int:id_envio>", methods=["POST"])
    def actualizar_envio(id_envio):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            cursor.execute("SELECT estado_envio FROM envios WHERE Id_envios = %s", (id_envio,))
            envio = cursor.fetchone()
            if envio:
                if envio['estado_envio'] == 'Entregado':
                    db.close()
                    return redirect(url_for('admin_envios'))
                estado_envio = request.form.get("estado_envio", "Por despachar")
                numero_guia = request.form.get("numero_guia", "")
                transportadora = request.form.get("transportadora", "Por asignar")
                cursor.execute(
                    "UPDATE envios SET estado_envio=%s, numero_guia=%s, transportadora=%s WHERE Id_envios=%s",
                    (estado_envio, numero_guia, transportadora, id_envio)
                )
                cursor.execute("SELECT Id_pedido FROM envios WHERE Id_envios=%s", (id_envio,))
                row = cursor.fetchone()
                if row:
                    if estado_envio == 'Enviado':
                        cursor.execute("UPDATE pedidos SET estado='Enviado' WHERE Id_pedido=%s", (row['Id_pedido'],))
                    elif estado_envio == 'Entregado':
                        cursor.execute("UPDATE pedidos SET estado='Entregado', metodo_pago='Pagado' WHERE Id_pedido=%s", (row['Id_pedido'],))
                    else:
                        cursor.execute("UPDATE pedidos SET estado='Pendiente' WHERE Id_pedido=%s", (row['Id_pedido'],))
                db.commit()
                cursor.execute("""
                    SELECT u.nombre, u.email, p.Id_pedido
                    FROM envios e
                    JOIN pedidos p ON e.Id_pedido = p.Id_pedido
                    JOIN usuarios u ON p.Id_usuario = u.Id_usuario
                    WHERE e.Id_envios = %s
                """, (id_envio,))
                datos = cursor.fetchone()
                if datos:
                    try:
                        if estado_envio == 'Enviado':
                            host_url = url_for('inicio', _external=True)
                            enviar_notificacion_despacho(mail, datos['nombre'], datos['email'], datos['Id_pedido'], transportadora, numero_guia, host_url)
                        elif estado_envio == 'Entregado':
                            enviar_agradecimiento_entrega(mail, datos['nombre'], datos['email'], datos['Id_pedido'])
                    except Exception as e:
                        print(f"Error al notificar cambio de envio: {e}")
            db.close()
        return redirect(url_for('admin_envios'))
