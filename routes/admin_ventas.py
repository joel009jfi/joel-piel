from datetime import datetime
from flask import render_template, request, redirect, session, url_for, jsonify
from db import conectar, obtener_cursor
from services.helpers import MESES_ES
from services.pdf_service import generar_reporte_ventas_pdf
from services.excel_service import exportar_ventas_excel


def register_routes(app):
    @app.route("/admin/ventas")
    def ver_ventas():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("""
            SELECT p.Id_pedido, p.total, p.estado, p.metodo_pago, p.fecha, u.nombre as cliente
            FROM pedidos p
            JOIN usuarios u ON p.Id_usuario = u.Id_usuario
            ORDER BY p.fecha DESC
        """)
        ventas_db = cursor.fetchall()
        db.close()
        meses = {}
        for v in ventas_db:
            if isinstance(v['fecha'], str):
                dt = datetime.strptime(v['fecha'], '%Y-%m-%d %H:%M:%S')
            else:
                dt = v['fecha']
            clave = f"{MESES_ES[dt.month]} {dt.year}"
            meses.setdefault(clave, []).append(v)
        meses_con_totales = {}
        for mes, ventas in meses.items():
            activas = [v for v in ventas if v['estado'] != 'Cancelado']
            total = sum(v['total'] for v in activas if v['total'] is not None)
            meses_con_totales[mes] = {'ventas': ventas, 'total': total, 'cantidad': len(ventas), 'activas': len(activas)}
        mes_actual = f"{MESES_ES[datetime.now().month]} {datetime.now().year}"
        return render_template("ventas_admin.html", meses=meses_con_totales, mes_actual=mes_actual)

    @app.route("/admin/ventas/eliminar/<int:id_pedido>", methods=["POST"])
    def eliminar_venta(id_pedido):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            try:
                cursor = db.cursor()
                cursor.execute("DELETE FROM envios WHERE Id_pedido = %s", (id_pedido,))
                cursor.execute("DELETE FROM pedidos WHERE Id_pedido = %s", (id_pedido,))
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error al eliminar pedido: {e}")
            finally:
                db.close()
        return redirect(url_for('ver_ventas'))

    @app.route("/admin/marcar-pagado/<int:id_pedido>", methods=["POST"])
    def marcar_pagado(id_pedido):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = db.cursor()
            cursor.execute("UPDATE pedidos SET estado = 'Pagado' WHERE Id_pedido = %s", (id_pedido,))
            db.commit()
            db.close()
        return redirect(url_for('ver_ventas'))

    @app.route("/admin/ventas/detalle/<int:id_pedido>")
    def detalle_venta(id_pedido):
        if session.get("rol") != "admin":
            return jsonify({"error": "No autorizado"}), 403
        db = conectar()
        if not db:
            return jsonify({"error": "Error de conexión"}), 500
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("""
            SELECT dp.Id_producto, dp.cantidad, dp.precio_unitario, p.nombre, p.imagen_url
            FROM detalle_pedido dp
            JOIN productos p ON dp.Id_producto = p.id_producto
            WHERE dp.Id_pedido = %s
        """, (id_pedido,))
        items = cursor.fetchall()
        db.close()
        return jsonify(items)

    @app.route("/admin/ventas/pdf")
    def reporte_ventas_pdf():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        mes_filtro = request.args.get("mes", "").strip()
        db = conectar()
        if not db:
            return "Error de conexión", 500
        cursor = obtener_cursor(db, diccionario=True)
        if mes_filtro and mes_filtro in MESES_ES:
            mes_num = MESES_ES.index(mes_filtro)
            ano = request.args.get("ano", datetime.now().year, type=int)
            cursor.execute("""
                SELECT p.Id_pedido, p.total, p.estado, p.fecha, u.nombre as cliente
                FROM pedidos p
                JOIN usuarios u ON p.Id_usuario = u.Id_usuario
                WHERE MONTH(p.fecha) = %s AND YEAR(p.fecha) = %s
                ORDER BY p.fecha DESC
            """, (mes_num, ano))
            titulo = f"Reporte {mes_filtro} {ano}"
        else:
            cursor.execute("""
                SELECT p.Id_pedido, p.total, p.estado, p.fecha, u.nombre as cliente
                FROM pedidos p
                JOIN usuarios u ON p.Id_usuario = u.Id_usuario
                ORDER BY p.fecha DESC
            """)
            titulo = "Reporte General"
        ventas = cursor.fetchall()
        gran_total = sum(v['total'] for v in ventas if v['total'] is not None) if ventas else 0
        db.close()
        fecha_generado = datetime.now().strftime("%d/%m/%Y %H:%M")
        return generar_reporte_ventas_pdf(ventas, titulo, fecha_generado, gran_total, mes_filtro)

    @app.route("/admin/ventas/excel")
    def reporte_ventas_excel():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error de conexión", 500
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("""
            SELECT p.Id_pedido, p.fecha, u.nombre as cliente, u.email, p.total, p.estado
            FROM pedidos p
            JOIN usuarios u ON p.Id_usuario = u.Id_usuario
            ORDER BY p.fecha DESC
        """)
        ventas = cursor.fetchall()
        db.close()
        return exportar_ventas_excel(ventas)
