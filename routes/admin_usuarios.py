from flask import render_template, request, redirect, session, url_for
from db import conectar, obtener_cursor


def register_routes(app):
    @app.route("/admin/usuarios")
    def admin_usuarios():
        """Lista de todos los usuarios registrados."""
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
