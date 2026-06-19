from flask import Flask, session
from config import Config
from extensions import mail, csrf
from services.helpers import datos_carrito
from models.carrito import asegurar_tabla_carrito

app = Flask(__name__)
app.config.from_object(Config)
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Control manual de CSRF
app.config['WTF_CSRF_TIME_LIMIT'] = 3600      # El token CSRF expira en 1 hora
csrf.init_app(app)
mail.init_app(app)
asegurar_tabla_carrito()


@app.context_processor
def inject_carrito():
    productos_carrito, total_carrito, cantidad_total_carrito = datos_carrito()
    return dict(
        productos_carrito=productos_carrito,
        total_carrito=total_carrito,
        cantidad_total_carrito=cantidad_total_carrito
    )


@app.template_test('numeric')
def is_numeric(value):
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

if __name__ == "__main__":
    app.run(debug=True)
