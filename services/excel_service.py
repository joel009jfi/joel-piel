import io
from datetime import datetime
from flask import make_response
import openpyxl


def exportar_ventas_excel(ventas):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ventas"
    ws.append(["ID Pedido", "Fecha", "Cliente", "Email", "Total", "Estado"])
    for v in ventas:
        fecha_str = v["fecha"].strftime('%d/%m/%Y %H:%M') if hasattr(v["fecha"], 'strftime') else v["fecha"]
        ws.append([
            v["Id_pedido"],
            fecha_str,
            v["cliente"],
            v["email"],
            float(v["total"]) if v["total"] else 0,
            v["estado"]
        ])
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    response = make_response(output.read())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = f'attachment; filename=ventas_joelpiel_{datetime.now().strftime("%Y%m%d")}.xlsx'
    return response


def generar_excel_pedidos():
    from db import conectar, obtener_cursor
    db = conectar()
    if not db:
        return "Error de conexión", 500
    cursor = obtener_cursor(db, diccionario=True)
    cursor.execute("""
        SELECT p.Id_pedido, p.total, p.estado, p.fecha, p.metodo_pago,
               u.nombre as cliente, u.email
        FROM pedidos p
        LEFT JOIN usuarios u ON p.Id_usuario = u.Id_usuario
        ORDER BY p.fecha DESC
    """)
    ventas = cursor.fetchall()
    db.close()
    return exportar_ventas_excel(ventas)
