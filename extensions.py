from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect

# Instancias compartidas — se vinculan a la app en app.py para evitar ciclos
mail = Mail()
csrf = CSRFProtect()
