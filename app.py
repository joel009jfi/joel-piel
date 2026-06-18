from flask import Flask, render_template, session
from config import Config
from extensions import mail, csrf
from services.helpers import datos_carrito
from models.carrito import asegurar_tabla_carrito

# Creación de la aplicación Flask y configuración desde la clase Config
app = Flask(__name__)
app.config.from_object(Config)
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Control manual de CSRF
app.config['WTF_CSRF_TIME_LIMIT'] = 3600      # El token CSRF expira en 1 hora
csrf.init_app(app)            # Activa CSRF en la app
mail.init_app(app)            # Activa el envío de correos
asegurar_tabla_carrito()      # Crea la tabla carrito si no existe


@app.context_processor
def inject_carrito():
    """Inyecta datos del carrito en TODAS las plantillas (sidebar, badge, etc.)."""
    productos_carrito, total_carrito, cantidad_total_carrito = datos_carrito()
    return dict(
        productos_carrito=productos_carrito,
        total_carrito=total_carrito,
        cantidad_total_carrito=cantidad_total_carrito
    )


@app.template_test('numeric')
def is_numeric(value):
    """Test de plantilla para detectar valores numéricos (usado en templates)."""
    return isinstance(value, (int, float))


# Importación de todas las rutas organizadas por módulo
from routes.auth import register_routes as register_auth
from routes.public import register_routes as register_public
from routes.carrito import register_routes as register_carrito
from routes.checkout import register_routes as register_checkout
from routes.contacto import register_routes as register_contacto
from routes.rastreo import register_routes as register_rastreo
from routes.pedidos_cliente import register_routes as register_pedidos
from routes.admin_dashboard import register_routes as register_admin_dashboard
from routes.admin_productos import register_routes as register_admin_productos
from routes.admin_ventas import register_routes as register_admin_ventas
from routes.admin_logistica import register_routes as register_admin_logistica
from routes.admin_usuarios import register_routes as register_admin_usuarios
from routes.admin_mensajes import register_routes as register_admin_mensajes

# Registro de todas las rutas en la aplicación
register_auth(app)
register_public(app)
register_carrito(app)
register_checkout(app)
register_contacto(app)
register_rastreo(app)
register_pedidos(app)
register_admin_dashboard(app)
register_admin_productos(app)
register_admin_ventas(app)
register_admin_logistica(app)
register_admin_usuarios(app)
register_admin_mensajes(app)


@app.errorhandler(404)
def not_found(e):
    """Página personalizada para errores 404 (ruta no encontrada)."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    """Página personalizada para errores 500 (error interno del servidor)."""
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)  # Inicia el servidor en modo desarrollo
