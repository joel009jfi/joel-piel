def test_inicio_ok(client):
    rv = client.get("/")
    assert rv.status_code == 200


def test_login_page(client):
    rv = client.get("/login")
    assert rv.status_code == 200
    assert b"Iniciar" in rv.data or b"login" in rv.data


def test_registro_page(client):
    rv = client.get("/registro")
    assert rv.status_code == 200
    assert b"Registrarse" in rv.data or b"registro" in rv.data


def test_olvide_contrasena_page(client):
    rv = client.get("/olvide-contrasena")
    assert rv.status_code == 200
    assert b"Recuperar" in rv.data or b"contrase" in rv.data


def test_mujer_page(client):
    rv = client.get("/mujer")
    assert rv.status_code == 200


def test_hombre_page(client):
    rv = client.get("/hombre")
    assert rv.status_code == 200


def test_lo_nuevo_page(client):
    rv = client.get("/lo-nuevo")
    assert rv.status_code == 200


def test_contacto_page(client):
    rv = client.get("/contacto")
    assert rv.status_code == 200


def test_rastrear_page(client):
    rv = client.get("/rastrear")
    assert rv.status_code == 200


def test_buscar_page(client):
    rv = client.get("/buscar?q=bolso")
    assert rv.status_code == 200


def test_carrito_page(client):
    rv = client.get("/carrito")
    assert rv.status_code == 200


def test_checkout_redirect_when_not_logged(client):
    rv = client.get("/carrito/checkout")
    assert rv.status_code == 302


def test_admin_redirect_when_not_logged(client):
    rv = client.get("/admin")
    assert rv.status_code == 302


def test_admin_ventas_redirect_when_not_logged(client):
    rv = client.get("/admin/ventas")
    assert rv.status_code == 302


def test_admin_productos_redirect_when_not_logged(client):
    rv = client.get("/admin/productos")
    assert rv.status_code == 302


def test_admin_envios_redirect_when_not_logged(client):
    rv = client.get("/admin/envios")
    assert rv.status_code == 302


def test_admin_usuarios_redirect_when_not_logged(client):
    rv = client.get("/admin/usuarios")
    assert rv.status_code == 302


def test_admin_mensajes_redirect_when_not_logged(client):
    rv = client.get("/admin/mensajes")
    assert rv.status_code == 302


def test_logout(client):
    rv = client.get("/logout")
    assert rv.status_code == 302


def test_404_page(client):
    rv = client.get("/ruta-inexistente-xyz")
    assert rv.status_code in (302, 404)
