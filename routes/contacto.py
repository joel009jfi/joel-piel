from flask import render_template, request, session, flash
from models.contacto import guardar_mensaje
from services.email_service import enviar_notificacion_contacto, enviar_confirmacion_contacto_cliente
from extensions import mail


def register_routes(app):
    @app.route("/contacto", methods=["GET", "POST"])
    def contacto():
        usuario = session.get("usuario")
        rol = session.get("rol")
        mensaje = ""
        error = False
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            email = request.form.get("email", "").strip()
            asunto = request.form.get("asunto", "otro")
            texto = request.form.get("mensaje", "").strip()
            if nombre and email and texto:
                try:
                    guardar_mensaje(nombre, email, asunto, texto)
                    enviar_notificacion_contacto(mail, nombre, email, asunto, texto)
                    try:
                        enviar_confirmacion_contacto_cliente(mail, nombre, email)
                    except Exception as e:
                        print(f"Error al enviar confirmación al cliente: {e}")
                    mensaje = "¡Mensaje enviado con éxito! Te responderemos pronto."
                    flash("¡Mensaje enviado con éxito! Te responderemos pronto.", "success")
                except Exception as e:
                    print(f"Error al enviar contacto: {e}")
                    mensaje = "Mensaje recibido. Nos pondremos en contacto contigo pronto."
                    flash("Mensaje recibido. Nos pondremos en contacto contigo pronto.", "success")
            else:
                mensaje = "Por favor completa todos los campos obligatorios."
                error = True
        return render_template("contacto.html", usuario=usuario, rol=rol, mensaje=mensaje, error=error)
