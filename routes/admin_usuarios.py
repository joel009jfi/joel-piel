from flask import render_template, request, redirect, session, url_for
import bcrypt
from db import conectar, obtener_cursor
from models.usuario import registrar_usuario, obtener_usuario_por_email
from services.email_service import enviar_bienvenida
from extensions import mail


def register_routes(app):
    @app.route("/admin/usuarios/crear", methods=["GET", "POST"])
    def admin_crear_usuario():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        mensaje = ""
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            rol = request.form.get("rol", "cliente")
            if not nombre or not email or not password:
                mensaje = "Todos los campos son obligatorios."
            elif obtener_usuario_por_email(email):
                mensaje = "Ese correo ya está registrado."
            else:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                if registrar_usuario(nombre, email, password_hash, rol):
                    try:
                        enviar_bienvenida(mail, nombre, email, url_for('inicio', _external=True))
                    except Exception as e:
                        print(f"Error al enviar correo de bienvenida: {e}")
                    return redirect(url_for('admin_usuarios'))
                mensaje = "Error al crear el usuario."
        return render_template("crear_usuario.html", mensaje=mensaje)
    @app.route("/admin/usuarios")
    def admin_usuarios():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT Id_usuario, nombre, email, rol FROM usuarios ORDER BY Id_usuario ASC")
        usuarios = cursor.fetchall()
        db.close()
        return render_template("usuarios_admin.html", usuarios=usuarios)

    @app.route("/admin/usuarios/editar/<int:id_usuario>", methods=["GET", "POST"])
    def editar_usuario_admin(id_usuario):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM usuarios WHERE Id_usuario = %s", (id_usuario,))
        usuario = cursor.fetchone()
        if not usuario:
            db.close()
            return redirect(url_for('admin_usuarios'))
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            email = request.form.get("email", "").strip()
            rol = request.form.get("rol", "cliente")
            cursor.execute("UPDATE usuarios SET nombre=%s, email=%s, rol=%s WHERE Id_usuario=%s",
                           (nombre, email, rol, id_usuario))
            db.commit()
            db.close()
            return redirect(url_for('admin_usuarios'))
        db.close()
        return render_template("editar_usuario.html", usuario=usuario)

    @app.route("/admin/usuarios/eliminar/<int:id_usuario>")
    def eliminar_usuario_admin(id_usuario):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM usuarios WHERE Id_usuario = %s", (id_usuario,))
            db.commit()
            db.close()
        return redirect(url_for('admin_usuarios'))

    @app.route("/admin/usuarios/cambiar-rol/<int:id_usuario>", methods=["POST"])
    def cambiar_rol_usuario(id_usuario):
        """Cambia el rol de un usuario entre admin y cliente."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db)
            cursor.execute("SELECT rol FROM usuarios WHERE Id_usuario = %s", (id_usuario,))
            usuario = cursor.fetchone()
            if usuario:
                # Alterna entre admin y cliente
                nuevo_rol = "cliente" if usuario[0] == "admin" else "admin"
                cursor.execute("UPDATE usuarios SET rol = %s WHERE Id_usuario = %s", (nuevo_rol, id_usuario))
                db.commit()
            db.close()
        return redirect(url_for('admin_usuarios'))
