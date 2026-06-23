from flask import render_template, request, redirect, session, url_for
import bcrypt
from itsdangerous import URLSafeTimedSerializer
from models.usuario import registrar_usuario, obtener_usuario_por_email
from models.carrito import cargar_carrito_db
from services.email_service import enviar_bienvenida, enviar_reset_password
from services.helpers import sincronizar_carrito_db
from extensions import mail
from config import Config


def register_routes(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        mensaje = ""
        if request.method == "POST":
            email = request.form["email"]
            password_ingresada = request.form["password"]
            usuario = obtener_usuario_por_email(email)
            if usuario:
                # Convierte el hash a bytes si viene como string
                hash_db = usuario["password"].encode('utf-8') if isinstance(usuario["password"], str) else usuario["password"]
                if bcrypt.checkpw(password_ingresada.encode('utf-8'), hash_db):
                    session["usuario"] = usuario["nombre"]
                    session["rol"] = usuario["rol"]
                    session["Id_usuario"] = usuario["Id_usuario"]
                    carrito_db = cargar_carrito_db(usuario["Id_usuario"])
                    session["carrito"] = carrito_db
                    return redirect(url_for('admin_panel')) if usuario["rol"] == "admin" else redirect(url_for('inicio'))
                mensaje = "Contraseña incorrecta."
            else:
                mensaje = "El correo no está registrado."
        return render_template("login.html", mensaje=mensaje)

    @app.route("/registro", methods=["GET", "POST"])
    def registro():
        mensaje = ""
        if request.method == "POST":
            nombre = request.form["nombre"]
            email = request.form["email"]
            password = request.form["password"]
            if obtener_usuario_por_email(email):
                mensaje = "Ese correo ya tiene una cuenta activa."
            else:
                # Genera hash bcrypt seguro antes de guardar
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                if registrar_usuario(nombre, email, password_hash):
                    usuario = obtener_usuario_por_email(email)
                    if usuario:
                        session["usuario"] = usuario["nombre"]
                        session["rol"] = usuario["rol"]
                        session["Id_usuario"] = usuario["Id_usuario"]
                        try:
                            enviar_bienvenida(mail, nombre, email, url_for('inicio', _external=True))
                        except Exception as e:
                            print(f"Error al enviar correo de bienvenida: {e}")
                    return redirect(url_for('inicio'))
                mensaje = "Hubo un error al guardar tus datos."
        return render_template("registro.html", mensaje=mensaje)

    @app.route("/logout")
    def logout():
        sincronizar_carrito_db()
        session.clear()
        return redirect(url_for('inicio'))

    @app.route("/olvide-contrasena", methods=["GET", "POST"])
    def olvide_contrasena():
        mensaje = ""
        if request.method == "POST":
            email = request.form.get("email", "")
            usuario = obtener_usuario_por_email(email)
            if usuario:
                s = URLSafeTimedSerializer(Config.SECRET_KEY)
                token = s.dumps(email, salt="reset-password")
                try:
                    enviar_reset_password(mail, usuario['nombre'], email, token, url_for('restablecer_contrasena', token=token, _external=True))
                    mensaje = "Te hemos enviado un enlace para restablecer tu contraseña. Revisa tu correo."
                except Exception as e:
                    print(f"Error enviando reset: {e}")
                    mensaje = "Error al enviar el correo. Intenta de nuevo."
            else:
                mensaje = "No encontramos una cuenta con ese correo."
        return render_template("olvide_contrasena.html", mensaje=mensaje)

    @app.route("/restablecer-contrasena/<token>", methods=["GET", "POST"])
    def restablecer_contrasena(token):
        mensaje = ""
        s = URLSafeTimedSerializer(Config.SECRET_KEY)
        try:
            email = s.loads(token, salt="reset-password", max_age=3600)
        except Exception:
            return render_template("restablecer_contrasena.html", valido=False)
        usuario = obtener_usuario_por_email(email)
        if not usuario:
            return render_template("restablecer_contrasena.html", valido=False)
        if request.method == "POST":
            from db import conectar, obtener_cursor
            password = request.form.get("password", "")
            if len(password) < 4:
                mensaje = "La contraseña debe tener al menos 4 caracteres."
            else:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                db = conectar()
                if db:
                    cursor = obtener_cursor(db)
                    cursor.execute("UPDATE usuarios SET password = %s WHERE email = %s", (password_hash, email))
                    db.commit()
                    db.close()
                    return render_template("restablecer_contrasena.html", valido=True, exito=True)
                mensaje = "Error de conexión."
        return render_template("restablecer_contrasena.html", valido=True, mensaje=mensaje)
