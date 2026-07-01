from flask import render_template, request, redirect, session, url_for
from db import conectar, obtener_cursor
from extensions import mail
from services.email_service import enviar_respuesta_contacto


def register_routes(app):
    @app.route("/admin/mensajes", methods=["GET", "POST"])
    def admin_mensajes():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)

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
                        cursor.execute("SELECT nombre, email FROM contactos WHERE id = %s", (id_mensaje,))
                        datos = cursor.fetchone()
                        cursor.execute("UPDATE contactos SET leido = 1, respuesta = %s WHERE id = %s",
                                       (respuesta, id_mensaje))
                        if datos:
                            try:
                                enviar_respuesta_contacto(mail, datos['nombre'], datos['email'], respuesta)
                            except Exception as e:
                                print(f"Error al enviar respuesta por correo: {e}")
                db.commit()

        cursor.execute("SELECT * FROM contactos ORDER BY fecha DESC")
        mensajes = cursor.fetchall()
        db.close()
        return render_template("mensajes_admin.html", mensajes=mensajes)

