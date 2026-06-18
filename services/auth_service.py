from functools import wraps
from flask import session, redirect, url_for
import bcrypt


def verificar_login(email, password, usuario):
    if not usuario:
        return "El correo no está registrado."
    # Asegura que el hash esté en bytes (viene como string desde MySQL)
    hash_db = usuario["password"].encode('utf-8') if isinstance(usuario["password"], str) else usuario["password"]
    if bcrypt.checkpw(password.encode('utf-8'), hash_db):
        session["usuario"] = usuario["nombre"]
        session["rol"] = usuario["rol"]
        session["Id_usuario"] = usuario["Id_usuario"]
        return None
    return "Contraseña incorrecta."


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("rol") != "admin":
            return redirect(url_for('inicio'))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
