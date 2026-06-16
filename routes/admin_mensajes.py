from flask import render_template, redirect, session, url_for
from models.contacto import obtener_mensajes


def register_routes(app):
    @app.route("/admin/mensajes")
    def admin_mensajes():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        mensajes = obtener_mensajes()
        return render_template("mensajes_admin.html", mensajes=mensajes)
