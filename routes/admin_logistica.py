from flask import render_template, request, redirect, session, url_for
from db import conectar, obtener_cursor


def register_routes(app):
    @app.route("/admin/envios")
    def admin_envios():
        """Panel de logística con todos los envíos y estado."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        # JOIN de envios, pedidos y usuarios para vista completa
        cursor.execute("""
            SELECT e.Id_envios, e.Id_pedido, e.direccion_envio, e.estado_envio,
                   e.numero_guia, e.transportadora, p.total, p.estado as estado_pago, p.fecha,
                   u.nombre as cliente
            FROM envios e
            JOIN pedidos p ON e.Id_pedido = p.Id_pedido
            JOIN usuarios u ON p.Id_usuario = u.Id_usuario
            ORDER BY e.Id_envios DESC
        """)
        envios = cursor.fetchall()
        db.close()
        return render_template("logistica_admin.html", envios=envios)

    @app.route("/admin/envios/actualizar/<int:id_envio>", methods=["POST"])
    def actualizar_envio(id_envio):
        """Actualiza el estado de envío, guía y transportadora."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db)
            # Verifica que el envío exista antes de actualizar
            cursor.execute("SELECT Id_pedido FROM envios WHERE Id_envios = %s", (id_envio,))
            envio = cursor.fetchone()
            if envio:
                estado_envio = request.form.get("estado_envio", "Por despachar")
                numero_guia = request.form.get("numero_guia", "")
                transportadora = request.form.get("transportadora", "Por asignar")
                cursor.execute(
                    "UPDATE envios SET estado_envio=%s, numero_guia=%s, transportadora=%s WHERE Id_envios=%s",
                    (estado_envio, numero_guia, transportadora, id_envio)
                )
                db.commit()
            db.close()
        return redirect(url_for('admin_envios'))
