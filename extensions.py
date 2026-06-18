from flask_mail import Mail      # Extensión para envío de correos SMTP
from flask_wtf.csrf import CSRFProtect  # Protección contra CSRF en formularios

# Instancias compartidas de extensiones Flask.
# Se declaran aquí (sin inicializar) y se vinculan a la app en app.py.
# Esto evita importaciones circulares entre módulos.
mail = Mail()
csrf = CSRFProtect()
