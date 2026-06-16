from flask import render_template, request, redirect, session, url_for
import bcrypt
from models.usuario import registrar_usuario, obtener_usuario_por_email
from models.carrito import cargar_carrito_db
from services.email_service import enviar_bienvenida
from services.helpers import sincronizar_carrito_db
from extensions import mail


def register_routes(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        mensaje = ""
        if request.method == "POST":
            email = request.form["email"]
            password_ingresada = request.form["password"]
            usuario = obtener_usuario_por_email(email)
            if usuario:
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
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                if registrar_usuario(nombre, email, password_hash):
                    mensaje = "¡Registro exitoso! Ya puedes iniciar sesión."
                    try:
                        enviar_bienvenida(mail, nombre, email, url_for('inicio', _external=True))
                    except Exception as e:
                        print(f"Error al enviar correo de bienvenida: {e}")
                else:
                    mensaje = "Hubo un error al guardar tus datos."
        return render_template("registro.html", mensaje=mensaje)

    @app.route("/logout")
    def logout():
        sincronizar_carrito_db()
        session.clear()
        return redirect(url_for('inicio'))
