from functools import wraps  # Para preservar metadatos de funciones decoradas
from flask import session, redirect, url_for
import bcrypt  # Hashing de contraseñas


def verificar_login(email, password, usuario):
    """Verifica credenciales contra el hash bcrypt. Retorna mensaje de error o None."""
    if not usuario:
        return "El correo no está registrado."
    # Asegura que el hash esté en bytes (viene como string desde MySQL)
    hash_db = usuario["password"].encode('utf-8') if isinstance(usuario["password"], str) else usuario["password"]
    if bcrypt.checkpw(password.encode('utf-8'), hash_db):
        # Credenciales correctas: guarda datos en la sesión
        session["usuario"] = usuario["nombre"]
        session["rol"] = usuario["rol"]
        session["Id_usuario"] = usuario["Id_usuario"]
        return None  # Sin error
    return "Contraseña incorrecta."


def admin_required(f):
    """Decorador: redirige al inicio si el usuario no es administrador."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    """Decorador: redirige al login si el usuario no ha iniciado sesión."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
