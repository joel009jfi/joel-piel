from flask import render_template, request, redirect, session, url_for
import bcrypt
from db import conectar, obtener_cursor
from models.usuario import registrar_usuario, eliminar_usuario_db
from services.email_service import enviar_creacion_cuenta_admin
from extensions import mail


def register_routes(app):
    @app.route("/admin/usuarios")
    def ver_usuarios():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT Id_usuario, nombre, email, rol FROM usuarios ORDER BY Id_usuario DESC")
        usuarios_db = cursor.fetchall()
        db.close()
        return render_template("usuarios_admin.html", usuarios=usuarios_db)

    @app.route("/admin/usuario/nuevo", methods=["GET", "POST"])
    def crear_usuario_admin():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        if request.method == "POST":
            nombre = request.form["nombre"]
            email = request.form["email"]
            password = request.form["password"]
            rol = request.form["rol"]
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            if registrar_usuario(nombre, email, password_hash, rol):
                try:
                    enviar_creacion_cuenta_admin(mail, nombre, email, rol)
                except Exception as e:
                    print(f"Error al enviar correo desde administración: {e}")
                return redirect(url_for('ver_usuarios'))
        return render_template("crear_usuario.html")

    @app.route("/admin/usuario/editar/<int:id_usuario>", methods=["GET", "POST"])
    def editar_usuario(id_usuario):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        cursor = obtener_cursor(db, diccionario=True)
        if request.method == "POST":
            nombre = request.form["nombre"]
            email = request.form["email"]
            rol = request.form["rol"]
            cursor.execute("UPDATE usuarios SET nombre=%s, email=%s, rol=%s WHERE Id_usuario=%s", (nombre, email, rol, id_usuario))
            db.commit()
            db.close()
            return redirect(url_for('ver_usuarios'))
        cursor.execute("SELECT * FROM usuarios WHERE Id_usuario = %s", (id_usuario,))
        usuario = cursor.fetchone()
        db.close()
        return render_template("editar_usuario.html", usuario=usuario)

    @app.route("/admin/usuario/eliminar/<int:id_usuario>")
    def eliminar_usuario(id_usuario):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        eliminar_usuario_db(id_usuario)
        return redirect(url_for('ver_usuarios'))
