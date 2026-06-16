import os
from flask import render_template, request, redirect, session, url_for, jsonify, current_app
from werkzeug.utils import secure_filename
from extensions import csrf
from db import conectar, obtener_cursor
from models.producto import obtener_categorias, registrar_producto, actualizar_stock_db, editar_producto_en_db, eliminar_producto_de_db
from services.helpers import allowed_file, stock_valido


def register_routes(app):
    @app.route("/admin/inventario")
    def ver_stock():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        busqueda = request.args.get("q", "").strip()
        db = conectar()
        if not db:
            return render_template("inventario_admin.html", productos=[], page=page, total_pages=1)
        cursor = obtener_cursor(db, diccionario=True)
        if busqueda:
            cursor.execute("SELECT COUNT(*) as total FROM productos WHERE LOWER(nombre) LIKE LOWER(%s)", (f"%{busqueda}%",))
            total = cursor.fetchone()['total']
            cursor.execute("SELECT id_producto, nombre, precio, stock, imagen_url FROM productos WHERE LOWER(nombre) LIKE LOWER(%s) ORDER BY id_producto DESC LIMIT %s OFFSET %s", (f"%{busqueda}%", per_page, offset))
        else:
            cursor.execute("SELECT COUNT(*) as total FROM productos")
            total = cursor.fetchone()['total']
            cursor.execute("SELECT id_producto, nombre, precio, stock, imagen_url FROM productos ORDER BY id_producto DESC LIMIT %s OFFSET %s", (per_page, offset))
        total_pages = max(1, (total + per_page - 1) // per_page)
        productos_db = cursor.fetchall()
        db.close()
        return render_template("inventario_admin.html", productos=productos_db, page=page, total_pages=total_pages, busqueda=busqueda)

    @app.route("/admin/inventario/update", methods=["POST"])
    @csrf.exempt
    def update_stock_ajax():
        if session.get("rol") != "admin":
            return jsonify({"error": "No authorized"}), 403
        datos = request.json
        if not datos:
            return jsonify({"error": "Se requiere JSON"}), 400
        id_producto = datos.get('id')
        nuevo_stock = datos.get('stock')
        if not stock_valido(nuevo_stock):
            return jsonify({"error": "Stock inválido"}), 400
        if actualizar_stock_db(id_producto, nuevo_stock):
            return jsonify({"success": True, "new_stock": nuevo_stock})
        return jsonify({"success": False}), 500

    @app.route("/admin/producto/nuevo", methods=["GET", "POST"])
    def nuevo_producto():
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        if request.method == "POST":
            nombre = request.form.get("nombre", "").strip()
            precio = request.form.get("precio")
            stock = request.form.get("stock")
            imagen_url = request.form.get("imagen_url", "").strip()
            id_categoria = request.form.get("id_categoria")
            descripcion = request.form.get("descripcion", "").strip()
            categorias = obtener_categorias()
            if not nombre or not precio or not stock or not id_categoria:
                return render_template("crear_producto.html", error="Todos los campos obligatorios deben completarse", categorias=categorias)
            try:
                precio_float = float(precio)
                stock_int = int(stock)
                if precio_float <= 0:
                    return render_template("crear_producto.html", error="El precio debe ser mayor a 0", categorias=categorias)
                if stock_int < 0:
                    return render_template("crear_producto.html", error="El stock no puede ser negativo", categorias=categorias)
            except (ValueError, TypeError):
                return render_template("crear_producto.html", error="Precio y stock deben ser valores numéricos", categorias=categorias)
            if 'imagen' in request.files:
                file = request.files['imagen']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    imagen_url = filename
            registrar_producto(nombre, precio_float, stock_int, imagen_url, id_categoria, descripcion)
            return redirect("/admin/inventario")
        categorias = obtener_categorias()
        return render_template("crear_producto.html", categorias=categorias)

    @app.route("/admin/producto/editar/<int:id_producto>", methods=["GET", "POST"])
    def editar_producto(id_producto):
        if session.get("rol") != "admin":
            return redirect("/")
        db = conectar()
        if not db:
            return redirect("/admin/inventario")
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
        producto = cursor.fetchone()
        if not producto:
            db.close()
            return redirect("/admin/inventario")
        if request.method == "POST":
            categorias = obtener_categorias()
            nombre = request.form.get("nombre", "").strip()
            precio = request.form.get("precio")
            stock = request.form.get("stock")
            imagen_url = request.form.get("imagen_url", "").strip()
            id_categoria = request.form.get("id_categoria")
            descripcion = request.form.get("descripcion", "").strip()
            if not nombre or not precio or not stock or not id_categoria:
                return render_template("editar_producto.html", producto=producto, categorias=categorias, error="Todos los campos obligatorios deben completarse")
            try:
                precio_float = float(precio)
                stock_int = int(stock)
                if precio_float <= 0:
                    return render_template("editar_producto.html", producto=producto, categorias=categorias, error="El precio debe ser mayor a 0")
                if stock_int < 0:
                    return render_template("editar_producto.html", producto=producto, categorias=categorias, error="El stock no puede ser negativo")
            except (ValueError, TypeError):
                return render_template("editar_producto.html", producto=producto, categorias=categorias, error="Precio y stock deben ser valores numéricos")
            if 'imagen' in request.files:
                file = request.files['imagen']
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                    imagen_url = filename
            editar_producto_en_db(id_producto, nombre, descripcion, precio_float, stock_int, imagen_url, id_categoria)
            db.close()
            return redirect("/admin/inventario")
        db.close()
        categorias = obtener_categorias()
        return render_template("editar_producto.html", producto=producto, categorias=categorias)

    @app.route("/admin/producto/eliminar/<int:id_producto>", methods=["POST", "GET"])
    def eliminar_producto_admin(id_producto):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        eliminar_producto_de_db(id_producto)
        return redirect(url_for('ver_stock'))
