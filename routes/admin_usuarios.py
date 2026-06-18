from flask import render_template, request, redirect, session, url_for
from db import conectar, obtener_cursor


def register_routes(app):
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
