from flask import render_template, request, redirect, session, url_for
from db import conectar, obtener_cursor
from services.email_service import enviar_notificacion_despacho
from extensions import mail


def register_routes(app):
    @app.route("/admin/logistica")
    def ver_envios():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            cursor.execute("""
                SELECT
                    p.Id_pedido, p.fecha, p.total, p.estado AS estado_pago,
                    u.nombre AS cliente, e.Id_envios, e.direccion_envio,
                    e.estado_envio, e.numero_guia, e.transportadora
                FROM pedidos p
                JOIN usuarios u ON p.Id_usuario = u.Id_usuario
                LEFT JOIN envios e ON p.Id_pedido = e.Id_pedido
                ORDER BY p.fecha DESC
            """)
            envios_db = cursor.fetchall()
            db.close()
        else:
            envios_db = []
        return render_template("logistica_admin.html", envios=envios_db)

    @app.route("/admin/despachar_pedido/<int:id_pedido>", methods=["POST"])
    def despachar_pedido(id_pedido):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        transportadora = request.form.get("transportadora")
        numero_guia = request.form.get("numero_guia")
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            try:
                cursor.execute("""
                    UPDATE envios
                    SET transportadora = %s, numero_guia = %s, estado_envio = 'Enviado'
                    WHERE Id_pedido = %s
                """, (transportadora, numero_guia, id_pedido))
                cursor.execute("""
                    UPDATE pedidos SET estado = 'Pagado'
                    WHERE Id_pedido = %s AND estado = 'Pendiente'
                """, (id_pedido,))
                db.commit()
                print(f"Pedido #{id_pedido} despachado por {transportadora} con guía {numero_guia}")
                cursor.execute("""
                    SELECT u.email, u.nombre FROM pedidos p
                    JOIN usuarios u ON p.Id_usuario = u.Id_usuario
                    WHERE p.Id_pedido = %s
                """, (id_pedido,))
                cliente = cursor.fetchone()
                if cliente:
                    try:
                        enviar_notificacion_despacho(mail, cliente['nombre'], cliente['email'], id_pedido, transportadora, numero_guia, request.host_url)
                    except Exception as e:
                        print(f"Error al enviar notificación de despacho: {e}")
            except Exception as e:
                db.rollback()
                print(f"Error al actualizar el despacho: {e}")
            finally:
                db.close()
        return redirect(url_for('ver_envios'))

    @app.route("/admin/entregar_pedido/<int:id_pedido>", methods=["POST"])
    def entregar_pedido(id_pedido):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            try:
                cursor.execute("UPDATE envios SET estado_envio = 'Entregado' WHERE Id_pedido = %s", (id_pedido,))
                db.commit()
                print(f"Pedido #{id_pedido} marcado como entregado con éxito.")
            except Exception as e:
                db.rollback()
                print(f"Error al marcar como entregado: {e}")
            finally:
                db.close()
        return redirect(url_for('ver_envios'))
