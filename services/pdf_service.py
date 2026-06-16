import io
from datetime import datetime
from flask import render_template, make_response
from xhtml2pdf import pisa


def generar_reporte_ventas_pdf(ventas, titulo, fecha_generado, gran_total, mes_filtro=""):
    rendered = render_template(
        'reporte_pdf.html',
        ventas=ventas,
        fecha_generado=fecha_generado,
        gran_total=gran_total,
        titulo=titulo
    )
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.BytesIO(rendered.encode("utf-8")), dest=result)
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        filename = mes_filtro.replace(" ", "_").lower() if mes_filtro else "reporte_general"
        response.headers['Content-Disposition'] = f'attachment; filename=ventas_{filename}_joelpiel.pdf'
        return response
    return "Hubo un error al generar el PDF", 500
