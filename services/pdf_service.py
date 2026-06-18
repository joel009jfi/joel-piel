import io  # Manejo de buffers en memoria
from datetime import datetime
from flask import render_template, make_response  # Respuesta HTTP desde template
from xhtml2pdf import pisa  # Conversor de HTML a PDF


def generar_reporte_ventas_pdf(ventas, titulo, fecha_generado, gran_total, mes_filtro=""):
    """Genera un PDF descargable con el reporte de ventas."""
    # Renderiza el template HTML como string
    rendered = render_template(
        'reporte_pdf.html',
        ventas=ventas,
        fecha_generado=fecha_generado,
        gran_total=gran_total,
        titulo=titulo
    )
    result = io.BytesIO()
    # Convierte el HTML renderizado a PDF en memoria
    pdf = pisa.CreatePDF(io.BytesIO(rendered.encode("utf-8")), dest=result)
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        # Nombre del archivo según el mes o genérico
        filename = mes_filtro.replace(" ", "_").lower() if mes_filtro else "reporte_general"
        response.headers['Content-Disposition'] = f'attachment; filename=ventas_{filename}_joelpiel.pdf'
        return response
    return "Hubo un error al generar el PDF", 500


def generar_pdf_pedido(id_pedido):
    """Genera y descarga el PDF de un pedido específico con sus productos."""
    from db import conectar, obtener_cursor
    db = conectar()
    if not db:
        return "Error de conexión", 500
    cursor = obtener_cursor(db, diccionario=True)
    cursor.execute("""
        SELECT p.Id_pedido, p.total, p.estado, p.fecha, p.metodo_pago,
               u.nombre, u.email, e.direccion_envio
        FROM pedidos p
        JOIN usuarios u ON p.Id_usuario = u.Id_usuario
        LEFT JOIN envios e ON p.Id_pedido = e.Id_pedido
        WHERE p.Id_pedido = %s
    """, (id_pedido,))
    pedido = cursor.fetchone()
    if not pedido:
        db.close()
        return "Pedido no encontrado", 404
    cursor.execute("""
        SELECT dp.cantidad, dp.precio_unitario, pr.nombre
        FROM detalle_pedido dp
        JOIN productos pr ON dp.Id_producto = pr.Id_producto
        WHERE dp.Id_pedido = %s
    """, (id_pedido,))
    pedido['productos'] = cursor.fetchall()
    db.close()
    rendered = render_template(
        'pedido_pdf.html',
        pedido=pedido,
        fecha_generado=datetime.now().strftime('%d/%m/%Y %H:%M')
    )
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.BytesIO(rendered.encode("utf-8")), dest=result)
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=pedido_{id_pedido}_joelpiel.pdf'
        return response
    return "Hubo un error al generar el PDF", 500
