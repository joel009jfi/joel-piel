import os
from werkzeug.utils import secure_filename  # Sanitiza nombres de archivos
from flask import render_template, request, redirect, session, url_for, current_app
from db import conectar, obtener_cursor
from models.producto import obtener_categorias


def register_routes(app):
    @app.route("/admin/productos")
    def admin_productos():
        """Lista de productos con paginación (25 por página)."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if not db:
            return "Error al conectar con la BD", 500
        cursor = obtener_cursor(db, diccionario=True)
        pagina = request.args.get("pagina", 1, type=int)
        por_pagina = 25
        offset = (pagina - 1) * por_pagina
        # Cuenta total para calcular páginas
        cursor.execute("SELECT COUNT(*) as total FROM productos")
        total_productos = cursor.fetchone()["total"]
        total_paginas = (total_productos + por_pagina - 1) // por_pagina  # Redondeo hacia arriba
        # Página actual de productos con nombre de categoría
        cursor.execute("""
            SELECT p.id_producto, p.nombre, p.precio, p.stock, p.imagen_url, c.nombre_categoria
            FROM productos p
            LEFT JOIN categorias c ON p.Id_categoria = c.Id_categoria
            ORDER BY p.id_producto DESC
            LIMIT %s OFFSET %s
        """, (por_pagina, offset))
        productos = cursor.fetchall()
        db.close()
        return render_template("inventario_admin.html", productos=productos, pagina=pagina, total_paginas=total_paginas)

    @app.route("/admin/productos/crear", methods=["GET", "POST"])
    def crear_producto():
        """Formulario para agregar un producto con imagen opcional."""
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
                filename = secure_filename(archivo.filename)  # Limpia el nombre del archivo
                upload_folder = current_app.root_path + "/static/img/"
                os.makedirs(upload_folder, exist_ok=True)  # Crea carpeta si no existe
                ruta = os.path.join(upload_folder, filename)
                archivo.save(ruta)
                imagen_url = filename  # Guarda solo el nombre, no la ruta
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
        """Formulario para editar un producto existente."""
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
            imagen_url = producto["imagen_url"]  # Mantiene la imagen actual por defecto
            archivo = request.files.get("imagen")
            if archivo and archivo.filename:
                filename = secure_filename(archivo.filename)
                upload_folder = current_app.root_path + "/static/img/"
                ruta = os.path.join(upload_folder, filename)
                archivo.save(ruta)
                imagen_url = filename  # Reemplaza con la nueva imagen
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
        """Elimina un producto de la base de datos."""
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        db = conectar()
        if db:
            cursor = obtener_cursor(db)
            cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
            db.commit()
            db.close()
        return redirect(url_for('admin_productos'))
