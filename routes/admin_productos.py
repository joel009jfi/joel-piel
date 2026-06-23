import os
from werkzeug.utils import secure_filename  # Sanitiza nombres de archivos
from flask import (
    render_template, request, redirect,
    session, url_for, current_app, jsonify
)
from db import conectar, obtener_cursor
from models.producto import obtener_categorias


def register_routes(app):
    @app.route("/admin/productos", methods=["GET", "POST"])
    def admin_productos():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        # Maneja petición POST JSON para actualizar stock
        if request.method == "POST" and request.is_json:
            try:
                data = request.get_json()
                id_producto = data.get("id")
                nuevo_stock = data.get("stock")
                if id_producto is None or nuevo_stock is None:
                    return jsonify({"success": False, "error": "Datos incompletos"}), 400
                db = conectar()
                if not db:
                    return jsonify({"success": False, "error": "Error de conexión"}), 500
                cursor = db.cursor()
                cursor.execute("UPDATE productos SET stock = %s WHERE id_producto = %s", (nuevo_stock, id_producto))
                db.commit()
                db.close()
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM categorias ORDER BY Id_categoria ASC")
        categorias = cursor.fetchall()
        cursor.execute("""
            SELECT p.id_producto, p.nombre, p.precio, p.stock, p.imagen_url, p.Id_categoria, c.nombre_categoria
            FROM productos p
            LEFT JOIN categorias c ON p.Id_categoria = c.Id_categoria
            ORDER BY c.Id_categoria ASC, p.nombre ASC
        """)
        productos = cursor.fetchall()
        db.close()
        agrupados = {}
        for cat in categorias:
            agrupados[cat['Id_categoria']] = {
                'nombre': cat['nombre_categoria'],
                'productos': [p for p in productos if p['Id_categoria'] == cat['Id_categoria']]
            }
        return render_template("inventario_admin.html", agrupados=agrupados)

    @app.route("/admin/productos/crear", methods=["GET", "POST"])
    def crear_producto():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        categorias = obtener_categorias()
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            precio = request.form.get("precio", type=float)
            stock = request.form.get("stock", type=int, default=0)
            descripcion = request.form.get("descripcion", "")
            id_categoria = request.form.get("id_categoria", type=int)
            imagen_url = ""
            archivo = request.files.get("imagen")
            if archivo and archivo.filename:
                filename = secure_filename(archivo.filename)
                upload_folder = current_app.root_path + "/static/img/"
                os.makedirs(upload_folder, exist_ok=True)
                ruta = os.path.join(upload_folder, filename)
                archivo.save(ruta)
                imagen_url = filename
            db = conectar()
            if db:
                cursor = obtener_cursor(db)
                cursor.execute("""
                    INSERT INTO productos (nombre, precio, stock, descripcion, imagen_url, Id_categoria)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (nombre, precio, stock, descripcion, imagen_url, id_categoria))
                db.commit()
                db.close()
                return redirect(url_for('admin_productos'))
            return "Error al conectar con la BD", 500
        return render_template("crear_producto.html", categorias=categorias)

    @app.route("/admin/productos/editar/<int:id_producto>", methods=["GET", "POST"])
    def editar_producto(id_producto):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        categorias = obtener_categorias()
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
        producto = cursor.fetchone()
        if not producto:
            db.close()
            return redirect(url_for('admin_productos'))
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            precio = request.form.get("precio", type=float)
            stock = request.form.get("stock", type=int, default=0)
            descripcion = request.form.get("descripcion", "")
            id_categoria = request.form.get("id_categoria", type=int)
            imagen_url = request.form.get("imagen_url", "").strip() or producto["imagen_url"]
            archivo = request.files.get("imagen")
            if archivo and archivo.filename:
                filename = secure_filename(archivo.filename)
                upload_folder = current_app.root_path + "/static/img/"
                ruta = os.path.join(upload_folder, filename)
                archivo.save(ruta)
                imagen_url = filename
            cursor.execute("""
                UPDATE productos SET nombre=%s, precio=%s, stock=%s, descripcion=%s, imagen_url=%s, Id_categoria=%s
                WHERE id_producto=%s
            """, (nombre, precio, stock, descripcion, imagen_url, id_categoria, id_producto))
            db.commit()
            db.close()
            return redirect(url_for('admin_productos'))
        db.close()
        return render_template("editar_producto.html", producto=producto, categorias=categorias)

    @app.route("/admin/productos/eliminar/<int:id_producto>")
    def eliminar_producto(id_producto):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db)
            cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
            db.commit()
            db.close()
        return redirect(url_for('admin_productos'))
