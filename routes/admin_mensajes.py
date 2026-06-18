from flask import render_template, redirect, session, url_for
from db import conectar, obtener_cursor


def register_routes(app):
    @app.route("/admin/mensajes")
    def admin_mensajes():
        """Bandeja de mensajes de contacto recibidos."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM contactos ORDER BY fecha DESC")
        mensajes = cursor.fetchall()
        db.close()
        return render_template("mensajes_admin.html", mensajes=mensajes)

    @app.route("/admin/mensajes/marcar-leido/<int:id_mensaje>")
    def marcar_leido(id_mensaje):
        """Marca un mensaje como leído."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db)
            # Cambia leido de 0 a 1
            cursor.execute("UPDATE contactos SET leido = 1 WHERE id = %s", (id_mensaje,))
            db.commit()
            db.close()
        return redirect(url_for('admin_mensajes'))
