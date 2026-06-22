from flask import render_template, request, session
from db import conectar, obtener_cursor


def register_routes(app):
    @app.route("/rastrear", methods=["GET", "POST"])
    def rastrear_pedido():
        usuario = session.get("usuario")
        rol = session.get("rol")
        resultado = None
        error = ""
        if request.method == "POST":
            pedido_id = request.form.get("pedido_id", "").strip()
            email = request.form.get("email", "").strip()
            if pedido_id and email:
                db = conectar()
                if db:
                    cursor = obtener_cursor(db, diccionario=True)
                    # Busca por número de pedido o por número de guía
                    cursor.execute("""
                        SELECT p.Id_pedido, p.total, p.estado, p.fecha,
                               e.estado_envio, e.transportadora, e.numero_guia,
                               u.nombre as cliente, u.email
                        FROM pedidos p
                        JOIN usuarios u ON p.Id_usuario = u.Id_usuario
                        LEFT JOIN envios e ON p.Id_pedido = e.Id_pedido
                        WHERE (p.Id_pedido = %s OR e.numero_guia = %s) AND u.email = %s
                    """, (pedido_id, pedido_id, email))
                    resultado = cursor.fetchone()
                    db.close()
                    if not resultado:
                        error = "No encontramos un pedido con ese número y correo."
                else:
                    error = "Error de conexión. Intenta de nuevo."
            else:
                error = "Ingresa el número de pedido o guía y tu correo electrónico."
        return render_template("rastrear.html", usuario=usuario, rol=rol, resultado=resultado, error=error)
