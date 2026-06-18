from flask import (
    render_template, request, session, redirect
)
from db import conectar, obtener_cursor
from models.producto import obtener_categorias


def register_routes(app):
    @app.route("/")
    def inicio():
        usuario = session.get("usuario")
        rol = session.get("rol")
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            cursor.execute("SELECT id_producto, nombre, precio, imagen_url, stock FROM productos ORDER BY id_producto DESC LIMIT 4")
            productos_db = cursor.fetchall()
            db.close()
        else:
            productos_db = []
        return render_template("index.html", usuario=usuario, rol=rol, productos=productos_db)

    @app.route("/mujer")
    def pagina_mujer():
        usuario = session.get("usuario")
        rol = session.get("rol")
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            cursor.execute("""
                SELECT p.id_producto, p.nombre, p.precio, p.imagen_url, p.stock
                FROM productos p
                WHERE p.Id_categoria IN (1, 3)  -- 1=Mujer, 3=Unisex
                ORDER BY p.id_producto DESC
            """)
            productos_db = cursor.fetchall()
            db.close()
        else:
            productos_db = []
        return render_template("mujer.html", usuario=usuario, rol=rol, productos=productos_db)

    @app.route("/hombre")
    def pagina_hombre():
        usuario = session.get("usuario")
        rol = session.get("rol")
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            cursor.execute("""
                SELECT p.id_producto, p.nombre, p.precio, p.imagen_url, p.stock
                FROM productos p
                WHERE p.Id_categoria IN (2, 3)  -- 2=Hombre, 3=Unisex
                ORDER BY p.id_producto DESC
            """)
            productos_db = cursor.fetchall()
            db.close()
        else:
            productos_db = []
        return render_template("hombre.html", usuario=usuario, rol=rol, productos=productos_db)

    @app.route("/lo-nuevo")
    def lo_nuevo():
        usuario = session.get("usuario")
        rol = session.get("rol")
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            cursor.execute("""
                SELECT id_producto, nombre, precio, imagen_url, stock
                FROM productos
                ORDER BY id_producto DESC
                LIMIT 8
            """)
            productos_db = cursor.fetchall()
            db.close()
        else:
            productos_db = []
        return render_template("lo_nuevo.html", usuario=usuario, rol=rol, productos=productos_db)

    @app.route("/buscar")
    def buscar():
        usuario = session.get("usuario")
        rol = session.get("rol")
        query = request.args.get("q", "").strip()
        precio_min = request.args.get("precio_min", type=float)
        precio_max = request.args.get("precio_max", type=float)
        categoria = request.args.get("categoria", type=int)
        productos_db = []
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            # Construye la consulta dinámicamente según los filtros aplicados
            sql = "SELECT id_producto, nombre, precio, imagen_url, stock FROM productos WHERE 1=1"
            params = []
            if query:
                sql += " AND LOWER(nombre) LIKE LOWER(%s)"  # Búsqueda insensible a mayúsculas
                params.append(f"%{query}%")
            if precio_min is not None:
                sql += " AND precio >= %s"
                params.append(precio_min)
            if precio_max is not None:
                sql += " AND precio <= %s"
                params.append(precio_max)
            if categoria:
                sql += " AND Id_categoria = %s"
                params.append(categoria)
            sql += " ORDER BY id_producto DESC"
            cursor.execute(sql, params)
            productos_db = cursor.fetchall()
            db.close()
        categorias = obtener_categorias()
        return render_template("buscar.html", usuario=usuario, rol=rol, query=query, productos=productos_db, categorias=categorias)

    @app.route("/producto/<int:id_producto>")
    def detalle_producto(id_producto):
        usuario = session.get("usuario")
        rol = session.get("rol")
        db = conectar()
        if not db:
            return redirect("/")
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT Id_categoria, nombre_categoria FROM categorias ORDER BY Id_categoria")
        categorias = {c["Id_categoria"]: c["nombre_categoria"] for c in cursor.fetchall()}
        cursor.execute("""
            SELECT id_producto, nombre, precio, stock, imagen_url, descripcion, Id_categoria
            FROM productos
            WHERE id_producto = %s
        """, (id_producto,))
        producto = cursor.fetchone()
        if not producto:
            db.close()
            return redirect("/")
        # Obtiene 4 productos aleatorios de la misma categoría (excluyendo el actual)
        cursor.execute("""
            SELECT id_producto, nombre, precio, imagen_url
            FROM productos
            WHERE Id_categoria = %s AND id_producto != %s
            ORDER BY RAND()
            LIMIT 4
        """, (producto['Id_categoria'], id_producto))
        relacionados = cursor.fetchall()
        db.close()
        return render_template("detalle_producto.html", usuario=usuario, rol=rol, producto=producto, relacionados=relacionados, categorias=categorias)
