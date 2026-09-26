# config.py - Configuración general de la aplicación Flask
import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    # Flask: clave secreta para firmar sesiones y tokens CSRF
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")

    # MySQL: parámetros de conexión a la base de datos
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "joel_piel")

    # SMTP: configuración del servidor de correo (Gmail)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))          # Puerto SSL de Gmail
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "true").lower() == "true"
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "joelpiel57@gmail.com")

    # Subida de imágenes: carpeta de destino y extensiones permitidas
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
