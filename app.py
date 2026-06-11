from flask import Flask, render_template, request, redirect, session, url_for, make_response, jsonify
from flask_mail import Mail, Message
from db import conectar, obtener_cursor, registrar_usuario, registrar_producto, actualizar_stock_db
from config import Config
import bcrypt
import io
from xhtml2pdf import pisa

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# --- CONFIGURACIÓN DE CORREO (GMAIL) desde Config ---
app.config['MAIL_SERVER'] = Config.MAIL_SERVER
app.config['MAIL_PORT'] = Config.MAIL_PORT
app.config['MAIL_USE_TLS'] = Config.MAIL_USE_TLS
app.config['MAIL_USE_SSL'] = Config.MAIL_USE_SSL
app.config['MAIL_USERNAME'] = Config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = Config.MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = Config.MAIL_DEFAULT_SENDER

mail = Mail(app)

# --- FUNCIÓN AUXILIAR: obtiene datos del carrito ---
def _datos_carrito():
    carrito = session.get("carrito", {})
    productos = []
    total = 0
    cantidad_total = 0

    db = conectar()
    if db:
        if carrito:
            cursor = obtener_cursor(db, diccionario=True)
            for id_producto, cantidad in carrito.items():
                cursor.execute("SELECT id_producto, nombre, precio, imagen_url, stock FROM productos WHERE id_producto = %s", (id_producto,))
                producto = cursor.fetchone()
                if producto:
                    producto['cantidad'] = cantidad
                    subtotal = float(producto['precio']) * cantidad
                    producto['subtotal'] = subtotal
                    total += subtotal
                    cantidad_total += cantidad
                    productos.append(producto)
        db.close()

    return productos, total, cantidad_total

# --- CONTEXT PROCESSOR: inyecta datos del carrito en TODAS las vistas ---
@app.context_processor
def inject_carrito():
    productos_carrito, total_carrito, cantidad_total_carrito = _datos_carrito()
    return dict(
        productos_carrito=productos_carrito,
        total_carrito=total_carrito,
        cantidad_total_carrito=cantidad_total_carrito
    )

@app.template_test('numeric')
def is_numeric(value):
    return isinstance(value, (int, float))

# --- PÁGINA PRINCIPAL ---
@app.route("/")
def inicio():
    usuario = session.get("usuario")
    rol = session.get("rol")

    db = conectar()
    if db:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("SELECT id_producto, nombre, precio, imagen_url FROM productos ORDER BY id_producto DESC LIMIT 4")
        productos_db = cursor.fetchall()
        db.close()
    else:
        productos_db = []

    return render_template("index.html", usuario=usuario, rol=rol, productos=productos_db)

# --- LOGIN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    mensaje = ""
    if request.method == "POST":
        email = request.form["email"]
        password_ingresada = request.form["password"]
        db = conectar()
        usuario = None
        if db:
            cursor = obtener_cursor(db)
            cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
            usuario = cursor.fetchone()
            db.close()
        else:
            mensaje = "Error de conexión con la base de datos."
        if usuario:
            hash_db = usuario["password"].encode('utf-8') if isinstance(usuario["password"], str) else usuario["password"]
            if bcrypt.checkpw(password_ingresada.encode('utf-8'), hash_db):
                session["usuario"] = usuario["nombre"]
                session["rol"] = usuario["rol"]
                return redirect(url_for('admin_panel')) if usuario["rol"] == "admin" else redirect(url_for('inicio'))
            mensaje = "Contraseña incorrecta."
        else:
            mensaje = "El correo no está registrado."
    return render_template("login.html", mensaje=mensaje)

# --- REGISTRO PÚBLICO (CON CORREO DE BIENVENIDA) ---
@app.route("/registro", methods=["GET", "POST"])
def registro():
    mensaje = ""
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]

        db = conectar()
        if not db:
            mensaje = "Error de conexión con la base de datos."
        else:
            cursor = obtener_cursor(db)
            cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))

            if cursor.fetchone():
                mensaje = "Ese correo ya tiene una cuenta activa."
                db.close()
            else:
                password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                if registrar_usuario(nombre, email, password_hash):
                    mensaje = "¡Registro exitoso! Ya puedes iniciar sesión."
                    db.close()

                    try:
                        msg = Message(
                            subject="¡Te damos la bienvenida a JOEL PIEL!",
                            recipients=[email]
                        )

                        msg.html = f"""
                        <div style="font-family: 'Montserrat', sans-serif; max-width: 600px; margin: 0 auto; padding: 30px; border: 1px solid #eee; border-radius: 4px;">
                            <div style="text-align: center; border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 25px;">
                                <h1 style="font-family: 'Playfair Display', serif; font-size: 26px; letter-spacing: 2px; margin: 0; color: #000;">JOEL PIEL</h1>
                                <p style="font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #666; margin: 5px 0 0 0;">Bienvenid@ a la familia</p>
                            </div>
                            <p style="font-size: 15px; color: #1c1a17; line-height: 1.6;">Hola <strong>{nombre}</strong>,</p>
                            <p style="font-size: 14px; color: #444; line-height: 1.6;">
                                Queremos darte una cálida bienvenida a nuestra comunidad. Tu cuenta ha sido creada correctamente en nuestra plataforma de manera segura.
                            </p>
                            <div style="text-align: center; margin: 35px 0;">
                                <a href="{url_for('inicio', _external=True)}" style="background-color: #000; color: #fff; text-decoration: none; padding: 13px 28px; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; display: inline-block;">
                                    Explorar la Colección
                                </a>
                            </div>
                        </div>
                        """
                        mail.send(msg)
                        print("¡Correo enviado con éxito!")

                    except Exception as e:
                        print(f"Error real al enviar correo de bienvenida: {e}")
                else:
                    mensaje = "Hubo un error al guardar tus datos."
                    db.close()
                
    return render_template("registro.html", mensaje=mensaje)

# --- PANEL ADMIN: DASHBOARD ---
@app.route("/admin")
def admin_panel():
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
    db = conectar()
    if not db:
        return render_template("admin.html", pedidos=[], total_ventas=0, pendientes=0)
    cursor = obtener_cursor(db, diccionario=True)
    
    cursor.execute("""
        SELECT p.Id_pedido, p.Id_usuario, p.total, p.estado, p.fecha, u.nombre as cliente 
        FROM pedidos p 
        LEFT JOIN usuarios u ON p.Id_usuario = u.Id_usuario 
        ORDER BY p.fecha DESC LIMIT 5
    """)
    pedidos_db = cursor.fetchall()
    
    cursor.execute("SELECT SUM(total) as gran_total FROM pedidos WHERE estado != 'Cancelado'")
    res_ventas = cursor.fetchone()
    total_ventas = res_ventas['gran_total'] if res_ventas and res_ventas['gran_total'] else 0
    
    cursor.execute("SELECT COUNT(*) as pendientes FROM pedidos WHERE estado = 'Pendiente'")
    res_pendientes = cursor.fetchone()
    conteo_pendientes = res_pendientes['pendientes'] if res_pendientes else 0
    
    db.close()
    return render_template("admin.html", pedidos=pedidos_db, total_ventas=total_ventas, pendientes=conteo_pendientes)

# --- CRUD USUARIOS: VER LISTA ---
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

# --- CRUD USUARIOS: CREAR NUEVO ---
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
                msg = Message(
                    subject="¡Tu cuenta en JOEL PIEL ha sido creada!",
                    recipients=[email]
                )
                msg.html = f"<h3>Hola {nombre}</h3><p>Tu cuenta con rol <strong>{rol}</strong> ha sido dada de alta.</p>"
                mail.send(msg)
            except Exception as e:
                print(f"Error al enviar correo desde administración: {e}")
                
            return redirect(url_for('ver_usuarios'))
            
    return render_template("crear_usuario.html")

# --- CRUD USUARIOS: EDITAR ---
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

# --- CRUD USUARIOS: ELIMINAR ---
@app.route("/admin/usuario/eliminar/<int:id_usuario>")
def eliminar_usuario(id_usuario):
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
    db = conectar()
    cursor = db.cursor()
    cursor.execute("DELETE FROM usuarios WHERE Id_usuario = %s", (id_usuario,))
    db.commit()
    db.close()
    return redirect(url_for('ver_usuarios'))

# --- VER TODAS LAS VENTAS ---
@app.route("/admin/ventas")
def ver_ventas():
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
    db = conectar()
    cursor = obtener_cursor(db, diccionario=True)
    cursor.execute("""
        SELECT p.Id_pedido, p.total, p.estado, p.fecha, u.nombre as cliente 
        FROM pedidos p 
        JOIN usuarios u ON p.Id_usuario = u.Id_usuario 
        ORDER BY p.fecha DESC
    """)
    ventas_db = cursor.fetchall()
    db.close()
    return render_template("ventas_admin.html", ventas=ventas_db)

# --- REPORTE PDF ---
@app.route("/admin/ventas/pdf")
def reporte_ventas_pdf():
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
    
    from datetime import datetime
    db = conectar()
    if not db:
        return "Error de conexión", 500
    cursor = obtener_cursor(db, diccionario=True)
    cursor.execute("""
        SELECT p.Id_pedido, p.total, p.estado, p.fecha, u.nombre as cliente 
        FROM pedidos p 
        JOIN usuarios u ON p.Id_usuario = u.Id_usuario 
        ORDER BY p.fecha DESC
    """)
    ventas = cursor.fetchall()
    gran_total = sum(v['total'] for v in ventas if v['total']) if ventas else 0
    db.close()
    
    fecha_generado = datetime.now().strftime("%d/%m/%Y %H:%M")
    rendered = render_template('reporte_pdf.html', ventas=ventas, fecha_generado=fecha_generado, gran_total=gran_total)
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.BytesIO(rendered.encode("utf-8")), dest=result)
    
    if not pdf.err:
        response = make_response(result.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=reporte_ventas_joelpiel.pdf'
        return response
    else:
        return "Hubo un error al generar el PDF", 500

# --- GESTIÓN DE PEDIDOS: ACTUALIZAR ESTADO ---
@app.route("/actualizar_estado/<int:id_pedido>/<nuevo_estado>")
def actualizar_estado(id_pedido, nuevo_estado):
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
    db = conectar()
    cursor = obtener_cursor(db)
    cursor.execute("UPDATE pedidos SET estado = %s WHERE Id_pedido = %s", (nuevo_estado, id_pedido))
    db.commit()
    db.close()
    return redirect(url_for('admin_panel'))


# =======================================================
#                   SECCIÓN INVENTARIO
# =======================================================
@app.route("/admin/inventario")
def ver_stock():
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
    db = conectar()
    cursor = obtener_cursor(db, diccionario=True)
    cursor.execute("SELECT id_producto, nombre, precio, stock, imagen_url FROM productos ORDER BY id_producto DESC")
    productos_db = cursor.fetchall()
    db.close()
    return render_template("inventario_admin.html", productos=productos_db)

@app.route("/admin/inventario/update", methods=["POST"])
def update_stock_ajax():
    if session.get("rol") != "admin":
        return jsonify({"error": "No authorized"}), 403
    
    id_producto = request.json.get('id')
    nuevo_stock = request.json.get('stock')
    
    if actualizar_stock_db(id_producto, nuevo_stock):
        return jsonify({"success": True, "new_stock": nuevo_stock})
    return jsonify({"success": False}), 500

@app.route("/admin/producto/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
    if request.method == "POST":
        nombre       = request.form.get("nombre")
        precio       = request.form.get("precio")
        stock        = request.form.get("stock")
        imagen_url   = request.form.get("imagen_url")
        id_categoria = request.form.get("id_categoria")
        descripcion  = request.form.get("descripcion", "")
 
        registrar_producto(nombre, precio, stock, imagen_url, id_categoria, descripcion)
        return redirect("/admin/inventario")
 
    return render_template("crear_producto.html")

@app.route("/admin/producto/eliminar/<int:id_producto>", methods=["POST", "GET"])
def eliminar_producto_admin(id_producto):
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
        
    db = conectar()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
            db.commit()
            print(f"Bolso con ID {id_producto} removido con éxito.")
        except Exception as e:
            print(f"Error interno al eliminar producto: {e}")
        finally:
            db.close()
            
    return redirect(url_for('ver_stock'))


# ==========================================
#           SECCIÓN LOGÍSTICA
# ==========================================
@app.route("/admin/logistica")
def ver_envios():
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
        
    db = conectar()
    if db:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("""
            SELECT 
                p.Id_pedido, 
                p.fecha, 
                p.total, 
                p.estado AS estado_pago, 
                u.nombre AS cliente,
                e.Id_envios,
                e.direccion_envio,
                e.estado_envio,
                e.numero_guia,
                e.transportadora
            FROM pedidos p 
            JOIN usuarios u ON p.Id_usuario = u.Id_usuario 
            LEFT JOIN envios e ON p.Id_pedido = e.Id_pedido
            ORDER BY p.fecha DESC
        """)
        envios_db = cursor.fetchall()
        db.close()
    else:
        envios_db = []
        
    return render_template("logistica_admin.html", envios=envios_db)

@app.route("/admin/despachar_pedido/<int:id_pedido>", methods=["POST"])
def despachar_pedido(id_pedido):
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
        
    transportadora = request.form.get("transportadora")
    numero_guia = request.form.get("numero_guia")
    
    db = conectar()
    if db:
        cursor = obtener_cursor(db, diccionario=True)
        try:
            cursor.execute("""
                UPDATE envios 
                SET transportadora = %s, numero_guia = %s, estado_envio = 'Enviado' 
                WHERE Id_pedido = %s
            """, (transportadora, numero_guia, id_pedido))
            
            cursor.execute("""
                UPDATE pedidos 
                SET estado = 'Pagado' 
                WHERE Id_pedido = %s AND estado = 'Pendiente'
            """, (id_pedido,))
            
            db.commit()
            print(f"Pedido #{id_pedido} despachado por {transportadora} con guía {numero_guia}")
            
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar el despacho: {e}")
        finally:
            db.close()
            
    return redirect(url_for('ver_envios'))

@app.route("/admin/entregar_pedido/<int:id_pedido>", methods=["POST"])
def entregar_pedido(id_pedido):
    if session.get("rol") != "admin":
        return redirect(url_for('inicio'))
        
    db = conectar()
    if db:
        cursor = obtener_cursor(db, diccionario=True)
        try:
            cursor.execute("""
                UPDATE envios 
                SET estado_envio = 'Entregado' 
                WHERE Id_pedido = %s
            """, (id_pedido,))
            
            db.commit()
            print(f"Pedido #{id_pedido} marcado como entregado con éxito.")
            
        except Exception as e:
            db.rollback()
            print(f"Error al marcar como entregado: {e}")
        finally:
            db.close()
            
    return redirect(url_for('ver_envios'))


# ==========================================
#           INTERFAZ DEL CARRITO
# ==========================================
@app.route("/carrito")
def ver_carrito():
    productos, total, _ = _datos_carrito()
    return render_template("carrito.html", productos=productos, total=total)

# --- AGREGAR PRODUCTO (BOTÓN + Y AGREGAR DEL HOME) ---
@app.route("/carrito/agregar/<int:id_producto>", methods=["GET", "POST"])
def agregar_al_carrito(id_producto):
    if "carrito" not in session:
        session["carrito"] = {}
        
    carrito = session["carrito"]
    id_str = str(id_producto)
    
    if id_str in carrito:
        carrito[id_str] += 1
    else:
        carrito[id_str] = 1
        
    session["carrito"] = carrito
    
    # Recalculamos los datos dinámicos actualizados
    productos_carrito, total_carrito, cantidad_total_carrito = _datos_carrito()
    
    # Buscamos el subtotal del producto modificado para pasárselo a JS
    nuevo_subtotal = 0
    for p in productos_carrito:
        if str(p['id_producto']) == id_str:
            nuevo_subtotal = p['subtotal']
            break

    return jsonify({
        "status": "success",
        "message": "Bolso agregado con éxito",
        "nueva_cantidad": carrito[id_str],
        "nuevo_subtotal": nuevo_subtotal,
        "total_carrito": total_carrito,
        "cantidad_total_carrito": cantidad_total_carrito,
        "producto_removido": False
    })

# --- NUEVA RUTA ASÍNCRONA: RESTAR PRODUCTO (BOTÓN -) ---
@app.route("/carrito/restar/<int:id_producto>", methods=["GET", "POST"])
def restar_del_carrito(id_producto):
    carrito = session.get("carrito", {})
    id_str = str(id_producto)
    producto_removido = False
    nueva_cantidad = 0
    nuevo_subtotal = 0
    
    if id_str in carrito:
        carrito[id_str] -= 1
        nueva_cantidad = carrito[id_str]
        
        if carrito[id_str] <= 0:
            del carrito[id_str]
            producto_removido = True
            
        session["carrito"] = carrito
        
    # Volvemos a calcular los totales globales de la bolsa
    productos_carrito, total_carrito, cantidad_total_carrito = _datos_carrito()
    
    # Buscamos el subtotal si el artículo todavía existe en el carro
    if not producto_removido:
        for p in productos_carrito:
            if str(p['id_producto']) == id_str:
                nuevo_subtotal = p['subtotal']
                break

    return jsonify({
        "status": "success",
        "nueva_cantidad": nueva_cantidad,
        "nuevo_subtotal": nuevo_subtotal,
        "total_carrito": total_carrito,
        "cantidad_total_carrito": cantidad_total_carrito,
        "producto_removido": producto_removido
    })

@app.route("/carrito/eliminar/<int:id_producto>")
def eliminar_del_carrito(id_producto):
    carrito = session.get("carrito", {})
    id_str = str(id_producto)
    
    if id_str in carrito:
        del carrito[id_str]
        session["carrito"] = carrito
        
    return redirect(url_for('inicio'))

# --- NUEVA RUTA: PANTALLA DE CHECKOUT (DATOS DE ENVÍO) ---
@app.route("/carrito/checkout")
def checkout():
    if "usuario" not in session:
        return redirect(url_for('login'))
        
    carrito = session.get("carrito", {})
    if not carrito:
        return redirect(url_for('inicio'))
        
    productos, total, cantidad = _datos_carrito()
    return render_template("checkout.html", productos=productos, total=total, cantidad_total=cantidad)

# --- PROCESAMIENTO FINAL DEL PEDIDO Y LOGÍSTICA ---
@app.route("/carrito/finalizar", methods=["POST"])
def finalizar_compra():
    if "usuario" not in session:
        return redirect(url_for('login'))
        
    carrito = session.get("carrito", {})
    if not carrito:
        return redirect(url_for('inicio'))
        
    db = conectar()
    if db:
        cursor = db.cursor(dictionary=True, buffered=True)
        
        cursor.execute("SELECT Id_usuario, email FROM usuarios WHERE nombre = %s", (session["usuario"],))
        usuario_db = cursor.fetchone()
        
        if not usuario_db:
            cursor.close()
            db.close()
            return "Error: Usuario no encontrado", 404
            
        id_usuario = usuario_db["Id_usuario"]
        email_usuario = usuario_db["email"]
        
        departamento = request.form.get("departamento", "Por definir")
        ciudad = request.form.get("ciudad", "Por definir")
        direccion_cruda = request.form.get("direccion", "Por definir")
        telefono = request.form.get("telefono", "")
        
        direccion_completa = f"{direccion_cruda}, {ciudad} - {departamento}. Tel: {telefono}"
        
        total = 0
        items_a_procesar = []
        
        for id_producto, cantidad in carrito.items():
            cursor.execute("SELECT id_producto, precio, stock FROM productos WHERE id_producto = %s", (id_producto,))
            prod = cursor.fetchone()
            if prod:
                if prod['stock'] < cantidad:
                    cursor.close()
                    db.close()
                    return "Lo sentimos, stock insuficiente para procesar la compra.", 400
                
                total += float(prod['precio']) * cantidad
                items_a_procesar.append({
                    'id': id_producto,
                    'nuevo_stock': prod['stock'] - cantidad
                })
        
        try:
            cursor.execute(
                "INSERT INTO pedidos (Id_usuario, total, estado, fecha) VALUES (%s, %s, 'Pendiente', NOW())",
                (id_usuario, total)
            )
            
            id_pedido_nuevo = cursor.lastrowid
            
            cursor.execute(
                """
                INSERT INTO envios (Id_pedido, direccion_envio, estado_envio, numero_guia, transportadora) 
                VALUES (%s, %s, 'Por despachar', 'Contraentrega', 'Por asignar')
                """,
                (id_pedido_nuevo, direccion_completa)
            )
            
            for item in items_a_procesar:
                cursor.execute("UPDATE productos SET stock = %s WHERE id_producto = %s", (item['nuevo_stock'], item['id']))
                
            db.commit()
            session.pop("carrito", None)

            try:
                msg = Message(
                    subject=f"Compra confirmada · Pedido #{id_pedido_nuevo} · JOEL PIEL",
                    recipients=[email_usuario]
                )
                msg.html = f"""
                <div style="font-family:'Montserrat',sans-serif;max-width:600px;margin:0 auto;padding:30px;">
                    <h1 style="font-family:'Playfair Display',serif;text-align:center;">JOEL PIEL</h1>
                    <p>Hola <strong>{session["usuario"]}</strong>,</p>
                    <p>Tu pedido <strong>#{id_pedido_nuevo}</strong> ha sido recibido y está siendo procesado.</p>
                    <p style="color:#666;">Te notificaremos cuando sea despachado. Si pagas contraentrega, ten el efectivo listo al recibir.</p>
                    <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
                    <p style="font-size:12px;color:#999;">JOEL PIEL · Envíos a todo Colombia</p>
                </div>
                """
                mail.send(msg)
            except Exception as e:
                print(f"Error al enviar confirmación de compra: {e}")

            return render_template("compra_exitosa.html", pedido_id=id_pedido_nuevo)
            
        except Exception as e:
            db.rollback()
            print(f"Error en la transacción de compra: {e}")
            return "Error interno al procesar la transacción", 500
        finally:
            cursor.close()
            db.close()
            
    return "Error de conexión con la base de datos", 500

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('inicio'))

# ==========================================
#   RUTAS NUEVAS - PEGAR EN app.py
#   Justo ANTES de la línea: if __name__ == "__main__":
# ==========================================

# --- PÁGINA MUJER ---
@app.route("/mujer")
def pagina_mujer():
    usuario = session.get("usuario")
    rol = session.get("rol")

    db = conectar()
    if db:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("""
            SELECT p.id_producto, p.nombre, p.precio, p.imagen_url
            FROM productos p
            WHERE p.Id_categoria IN (1, 3)
            ORDER BY p.id_producto DESC
        """)
        productos_db = cursor.fetchall()
        db.close()
    else:
        productos_db = []

    return render_template("mujer.html", usuario=usuario, rol=rol, productos=productos_db)


# --- PÁGINA HOMBRE ---
@app.route("/hombre")
def pagina_hombre():
    usuario = session.get("usuario")
    rol = session.get("rol")

    db = conectar()
    if db:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("""
            SELECT p.id_producto, p.nombre, p.precio, p.imagen_url
            FROM productos p
            WHERE p.Id_categoria IN (2, 3)
            ORDER BY p.id_producto DESC
        """)
        productos_db = cursor.fetchall()
        db.close()
    else:
        productos_db = []

    return render_template("hombre.html", usuario=usuario, rol=rol, productos=productos_db)

# --- PÁGINA LO NUEVO (últimos 8 productos registrados) ---
@app.route("/lo-nuevo")
def lo_nuevo():
    usuario = session.get("usuario")
    rol = session.get("rol")

    db = conectar()
    if db:
        cursor = obtener_cursor(db, diccionario=True)
        cursor.execute("""
            SELECT id_producto, nombre, precio, imagen_url 
            FROM productos 
            ORDER BY id_producto DESC 
            LIMIT 8
        """)
        productos_db = cursor.fetchall()
        db.close()
    else:
        productos_db = []

    return render_template("lo_nuevo.html", usuario=usuario, rol=rol, productos=productos_db)


# --- BUSCADOR ---
@app.route("/buscar")
def buscar():
    usuario = session.get("usuario")
    rol = session.get("rol")
    query = request.args.get("q", "").strip()

    productos_db = []
    if query:
        db = conectar()
        if db:
            cursor = obtener_cursor(db, diccionario=True)
            termino = f"%{query}%"
            cursor.execute("""
                SELECT id_producto, nombre, precio, imagen_url 
                FROM productos 
                WHERE LOWER(nombre) LIKE LOWER(%s)
                ORDER BY id_producto DESC
            """, (termino,))
            productos_db = cursor.fetchall()
            db.close()

    return render_template("buscar.html", usuario=usuario, rol=rol, query=query, productos=productos_db)


# --- CONTACTO ---
@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    usuario = session.get("usuario")
    rol = session.get("rol")
    mensaje = ""
    error = False

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        asunto = request.form.get("asunto", "otro")
        texto = request.form.get("mensaje", "").strip()

        if nombre and email and texto:
            try:
                msg = Message(
                    subject=f"[JOEL PIEL - Contacto] {asunto.capitalize()} · {nombre}",
                    recipients=["joelpiel57@gmail.com"]
                )
                msg.html = f"""
                <div style="font-family:'Montserrat',sans-serif;max-width:600px;margin:0 auto;padding:30px;border:1px solid #eee;">
                    <h2 style="font-family:'Playfair Display',serif;margin-bottom:20px;">Nuevo mensaje de contacto</h2>
                    <p><strong>Nombre:</strong> {nombre}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Asunto:</strong> {asunto}</p>
                    <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
                    <p style="color:#333;line-height:1.6;">{texto}</p>
                </div>
                """
                mail.send(msg)
                mensaje = "¡Mensaje enviado con éxito! Te responderemos pronto."
            except Exception as e:
                print(f"Error al enviar contacto: {e}")
                mensaje = "Mensaje recibido. Nos pondremos en contacto contigo pronto."
        else:
            mensaje = "Por favor completa todos los campos obligatorios."
            error = True

    return render_template("contacto.html", usuario=usuario, rol=rol, mensaje=mensaje, error=error)


# ============================================================
#  Ruta de detalle de producto
 
@app.route("/producto/<int:id_producto>")
def detalle_producto(id_producto):
    usuario = session.get("usuario")
    rol = session.get("rol")

    db = conectar()
    if not db:
        return redirect("/")

    cursor = obtener_cursor(db, diccionario=True)
    cursor.execute("""
        SELECT id_producto, nombre, precio, stock, imagen_url, descripcion, Id_categoria
        FROM productos
        WHERE id_producto = %s
    """, (id_producto,))
    producto = cursor.fetchone()

    if not producto:
        db.close()
        return redirect("/")

    cursor.execute("""
        SELECT id_producto, nombre, precio, imagen_url
        FROM productos
        WHERE Id_categoria = %s AND id_producto != %s
        ORDER BY RAND()
        LIMIT 4
    """, (producto['Id_categoria'], id_producto))
    relacionados = cursor.fetchall()
    db.close()

    return render_template("detalle_producto.html", usuario=usuario, rol=rol, producto=producto, relacionados=relacionados)

#  Rutas para editar producto
# ============================================================
 
@app.route("/admin/producto/editar/<int:id_producto>", methods=["GET", "POST"])
def editar_producto(id_producto):
    if session.get("rol") != "admin":
        return redirect("/")
 
    db = conectar()
    if not db:
        return redirect("/admin/inventario")
 
    cursor = obtener_cursor(db, diccionario=True)
 
    if request.method == "POST":
        nombre       = request.form.get("nombre")
        precio       = request.form.get("precio")
        stock        = request.form.get("stock")
        imagen_url   = request.form.get("imagen_url")
        id_categoria = request.form.get("id_categoria")
        descripcion  = request.form.get("descripcion", "")
 
        cursor.execute("""
            UPDATE productos 
            SET nombre=%s, precio=%s, stock=%s, imagen_url=%s, Id_categoria=%s, descripcion=%s
            WHERE id_producto=%s
        """, (nombre, precio, stock, imagen_url, id_categoria, descripcion, id_producto))
        db.commit()
        db.close()
        return redirect("/admin/inventario")
 
    # GET — cargar datos actuales del producto
    cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id_producto,))
    producto = cursor.fetchone()
    db.close()
    
    if not producto:
        return redirect("/admin/inventario")
 
    return render_template("editar_producto.html", producto=producto)
 
if __name__ == "__main__":
    app.run(debug=True)