from flask_mail import Message


def enviar_bienvenida(mail, nombre, email, url_inicio):
    try:
        msg = Message(subject="¡Te damos la bienvenida a JOEL PIEL!", recipients=[email])
        msg.html = f"""
        <div style="font-family: 'Montserrat', sans-serif; max-width: 600px; margin: 0 auto; padding: 30px; border: 1px solid #eee; border-radius: 4px;">
            <div style="text-align: center; border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 25px;">
                <h1 style="font-family: 'Playfair Display', serif; font-size: 26px; letter-spacing: 2px; margin: 0; color: #000;">JOEL PIEL</h1>
                <p style="font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #666; margin: 5px 0 0 0;">Bienvenid@ a la familia</p>
            </div>
            <p style="font-size: 15px; color: #1c1a17; line-height: 1.6;">Hola <strong>{nombre}</strong>,</p>
            <p style="font-size: 14px; color: #444; line-height: 1.6;">Queremos darte una cálida bienvenida a nuestra comunidad. Tu cuenta ha sido creada correctamente en nuestra plataforma de manera segura.</p>
            <div style="text-align: center; margin: 35px 0;">
                <a href="{url_inicio}" style="background-color: #000; color: #fff; text-decoration: none; padding: 13px 28px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; display: inline-block;">Explorar la Colección</a>
            </div>
        </div>
        """
        mail.send(msg)
        print("¡Correo de bienvenida enviado con éxito!")
    except Exception as e:
        print(f"Error al enviar correo de bienvenida: {e}")


def enviar_confirmacion_compra(mail, usuario, email, id_pedido, metodo_pago):
    try:
        msg = Message(subject=f"Compra confirmada · Pedido #{id_pedido} · JOEL PIEL", recipients=[email])
        msg.html = f"""
        <div style="font-family:'Montserrat',sans-serif;max-width:600px;margin:0 auto;padding:30px;">
            <h1 style="font-family:'Playfair Display',serif;text-align:center;">JOEL PIEL</h1>
            <p>Hola <strong>{usuario}</strong>,</p>
            <p>Tu pedido <strong>#{id_pedido}</strong> ha sido confirmado.</p>
            <p><strong>Método de pago:</strong> {"Pago en línea" if metodo_pago == "Completo" else "Contraentrega"}</p>
            <p style="color:#666;">El envío (<strong>$15,000/kg</strong>) se paga directamente a la transportadora al recibir el paquete.</p>
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="font-size:12px;color:#999;">JOEL PIEL · Envíos a todo Colombia</p>
        </div>
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar confirmación de compra: {e}")


def enviar_notificacion_contacto(mail, nombre, email, asunto, texto, email_admin="joelpiel57@gmail.com"):
    try:
        msg = Message(subject=f"[JOEL PIEL - Contacto] {asunto.capitalize()} · {nombre}", recipients=[email_admin])
        msg.html = f"""
        <div style="font-family:'Montserrat',sans-serif;max-width:600px;margin:0 auto;padding:30px;border:1px solid #eee;">
            <h2 style="font-family:'Playfair Display',serif;margin-bottom:20px;">Nuevo mensaje de contacto</h2>
            <p><strong>Nombre:</strong> {nombre}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Asunto:</strong> {asunto}</p>
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="color:#333;line-height:1.6;">{texto}</p>
        </div>
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar notificación de contacto: {e}")


def enviar_notificacion_despacho(mail, cliente_nombre, cliente_email, id_pedido, transportadora, numero_guia, host_url):
    try:
        msg = Message(subject=f"Tu pedido #{id_pedido} está en camino · JOEL PIEL", recipients=[cliente_email])
        msg.html = f"""
        <div style="font-family:'Montserrat',sans-serif;max-width:600px;margin:0 auto;padding:30px;">
            <h1 style="font-family:'Playfair Display',serif;text-align:center;">JOEL PIEL</h1>
            <p>Hola <strong>{cliente_nombre}</strong>,</p>
            <p>Tu pedido <strong>#{id_pedido}</strong> ha sido despachado.</p>
            <p style="background:#f9f9f9;padding:15px;border-left:3px solid #000;">
                <strong>Transportadora:</strong> {transportadora}<br>
                <strong>Guía:</strong> {numero_guia}
            </p>
            <p>El costo del envío (<strong>$15,000/kg</strong>) se paga directamente a la transportadora al recibir el paquete.</p>
            <p>Puedes rastrear tu pedido en <a href="{host_url}rastrear">{host_url}rastrear</a>.</p>
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="font-size:12px;color:#999;">JOEL PIEL · Envíos a todo Colombia</p>
        </div>
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar notificación de despacho: {e}")


def enviar_notificacion_pago(mail, nombre, email, id_pedido):
    try:
        msg = Message(subject=f"Pago confirmado · Pedido #{id_pedido} · JOEL PIEL", recipients=[email])
        msg.html = f"""
        <div style="font-family:'Montserrat',sans-serif;max-width:600px;margin:0 auto;padding:30px;">
            <h1 style="font-family:'Playfair Display',serif;text-align:center;">JOEL PIEL</h1>
            <p>Hola <strong>{nombre}</strong>,</p>
            <p>El pago de tu pedido <strong>#{id_pedido}</strong> ha sido confirmado.</p>
            <p>Pronto recibirás la información de despacho.</p>
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="font-size:12px;color:#999;">JOEL PIEL · Envíos a todo Colombia</p>
        </div>
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar notificación de pago: {e}")


def enviar_respuesta_contacto(mail, nombre, email, respuesta):
    try:
        msg = Message(subject="Respuesta a tu consulta · JOEL PIEL", recipients=[email])
        msg.html = f"""
        <div style="font-family:'Montserrat',sans-serif;max-width:600px;margin:0 auto;padding:30px;border:1px solid #eee;border-radius:4px;">
            <div style="text-align:center;border-bottom:1px solid #eee;padding-bottom:20px;margin-bottom:25px;">
                <h1 style="font-family:'Playfair Display',serif;font-size:26px;letter-spacing:2px;margin:0;color:#000;">JOEL PIEL</h1>
            </div>
            <p style="font-size:15px;color:#1c1a17;">Hola <strong>{nombre}</strong>,</p>
            <p style="font-size:14px;color:#444;line-height:1.6;">Hemos dado respuesta a tu solicitud:</p>
            <div style="background:#f9f9f9;padding:20px;border-left:3px solid #000;margin:20px 0;font-size:14px;color:#333;line-height:1.6;">
                {respuesta}
            </div>
            <p style="font-size:14px;color:#444;line-height:1.6;">Gracias por escribirnos. Si tienes más preguntas, no dudes en contactarnos nuevamente.</p>
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="font-size:12px;color:#999;text-align:center;">JOEL PIEL · Envíos a todo Colombia</p>
        </div>
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar respuesta de contacto: {e}")


def enviar_confirmacion_contacto_cliente(mail, nombre, email):
    try:
        msg = Message(subject="Hemos recibido tu mensaje · JOEL PIEL", recipients=[email])
        msg.html = f"""
        <div style="font-family:'Montserrat',sans-serif;max-width:600px;margin:0 auto;padding:30px;border:1px solid #eee;border-radius:4px;">
            <div style="text-align:center;border-bottom:1px solid #eee;padding-bottom:20px;margin-bottom:25px;">
                <h1 style="font-family:'Playfair Display',serif;font-size:26px;letter-spacing:2px;margin:0;color:#000;">JOEL PIEL</h1>
            </div>
            <p style="font-size:15px;color:#1c1a17;">Hola <strong>{nombre}</strong>,</p>
            <p style="font-size:14px;color:#444;line-height:1.6;">Hemos recibido tu mensaje correctamente. Nuestro equipo lo revisará y te responderemos a la brevedad posible.</p>
            <p style="font-size:14px;color:#444;line-height:1.6;">Gracias por contactarnos.</p>
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="font-size:12px;color:#999;text-align:center;">JOEL PIEL · Envíos a todo Colombia</p>
        </div>
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar confirmación de contacto: {e}")


def enviar_creacion_cuenta_admin(mail, nombre, email, rol):
    try:
        msg = Message(subject="¡Tu cuenta en JOEL PIEL ha sido creada!", recipients=[email])
        msg.html = f"<h3>Hola {nombre}</h3><p>Tu cuenta con rol <strong>{rol}</strong> ha sido dada de alta.</p>"
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar correo desde administración: {e}")


def enviar_agradecimiento_entrega(mail, nombre, email, id_pedido):
    try:
        msg = Message(subject=f"¡Gracias por tu compra · Pedido #{id_pedido} · JOEL PIEL", recipients=[email])
        msg.html = f"""
        <div style="font-family:'Montserrat',sans-serif;max-width:600px;margin:0 auto;padding:30px;border:1px solid #eee;border-radius:4px;">
            <div style="text-align:center;border-bottom:1px solid #eee;padding-bottom:20px;margin-bottom:25px;">
                <h1 style="font-family:'Playfair Display',serif;font-size:26px;letter-spacing:2px;margin:0;color:#000;">JOEL PIEL</h1>
            </div>
            <p style="font-size:15px;color:#1c1a17;line-height:1.6;">Hola <strong>{nombre}</strong>,</p>
            <p style="font-size:14px;color:#444;line-height:1.6;">¡Gracias por tu compra! Queremos confirmarte que tu pedido <strong>#{id_pedido}</strong> ha sido entregado exitosamente.</p>
            <p style="font-size:14px;color:#444;line-height:1.6;">Esperamos que disfrutes mucho tu producto. Agradecemos tu preferencia y confianza en nosotros.</p>
            <div style="text-align:center;margin:35px 0;">
                <p style="font-size:14px;color:#444;line-height:1.6;">Si tienes alguna pregunta o comentario, no dudes en escribirnos. ¡Estaremos encantados de ayudarte!</p>
            </div>
            <p style="font-size:14px;color:#444;line-height:1.6;">Con cariño,</p>
            <p style="font-size:14px;color:#000;font-weight:600;">El equipo de JOEL PIEL</p>
            <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
            <p style="font-size:12px;color:#999;text-align:center;">JOEL PIEL · Envíos a todo Colombia</p>
        </div>
        """
        mail.send(msg)
    except Exception as e:
        print(f"Error al enviar agradecimiento por entrega: {e}")
