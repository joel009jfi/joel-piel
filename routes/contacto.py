from flask import render_template, request, session
from models.contacto import guardar_mensaje
from services.email_service import enviar_notificacion_contacto
from extensions import mail


def register_routes(app):
    @app.route("/contacto", methods=["GET", "POST"])
    def contacto():
        """Formulario de contacto: guarda en BD y envía email al administrador."""
        usuario = session.get("usuario")
        rol = session.get("rol")
        mensaje = ""
        error = False
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            email = request.form.get("email", "").strip()
            asunto = request.form.get("asunto", "otro")
            texto = request.form.get("mensaje", "").strip()
            if nombre and email and texto:  # Validación básica de campos obligatorios
                try:
                    guardar_mensaje(nombre, email, asunto, texto)
                    enviar_notificacion_contacto(mail, nombre, email, asunto, texto)
                    mensaje = "¡Mensaje enviado con éxito! Te responderemos pronto."
                except Exception as e:
                    print(f"Error al enviar contacto: {e}")
                    mensaje = "Mensaje recibido. Nos pondremos en contacto contigo pronto."
            else:
                mensaje = "Por favor completa todos los campos obligatorios."
                error = True
        return render_template("contacto.html", usuario=usuario, rol=rol, mensaje=mensaje, error=error)
