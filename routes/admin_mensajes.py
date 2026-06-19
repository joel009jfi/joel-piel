from flask import render_template, request, redirect, session, url_for
from db import conectar, obtener_cursor


def register_routes(app):
    @app.route("/admin/mensajes", methods=["GET", "POST"])
    def admin_mensajes():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)

        # Limpia mensajes con más de 7 días
        cursor.execute("DELETE FROM contactos WHERE fecha < NOW() - INTERVAL 7 DAY")
        db.commit()

        if request.method == "POST":
            id_mensaje = request.form.get("id_mensaje", type=int)
            accion = request.form.get("accion")
            if id_mensaje:
                if accion == "leido":
                    cursor.execute("UPDATE contactos SET leido = 1 WHERE id = %s", (id_mensaje,))
                elif accion == "responder":
                    respuesta = request.form.get("respuesta", "").strip()
                    if respuesta:
                        cursor.execute("UPDATE contactos SET leido = 1, respuesta = %s WHERE id = %s",
                                       (respuesta, id_mensaje))
                db.commit()

        cursor.execute("SELECT * FROM contactos ORDER BY fecha DESC")
        mensajes = cursor.fetchall()
        db.close()
        return render_template("mensajes_admin.html", mensajes=mensajes)

    @app.route("/admin/mensajes/marcar-leido/<int:id_mensaje>")
    def marcar_leido(id_mensaje):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db)
            cursor.execute("UPDATE contactos SET leido = 1 WHERE id = %s", (id_mensaje,))
            db.commit()
            db.close()
        return redirect(url_for('admin_mensajes'))
