"""Control de acceso: quién puede hacer qué."""
import pytest

from tests.helpers import bearer

API = "/api/v1"

# (método, ruta, cuerpo): operaciones que SOLO puede hacer un administrador
SOLO_ADMIN = [
    ("post", f"{API}/productos/", {"codigo_interno": "X", "titulo": "X", "categoria_id": 1, "costo_actual": "1", "precio_venta": "2"}),
    ("patch", f"{API}/productos/1", {"titulo": "Y"}),
    ("post", f"{API}/categorias/", {"nombre": "X"}),
    ("patch", f"{API}/categorias/1", {"nombre": "Y"}),
    ("post", f"{API}/subcategorias/", {"nombre": "X", "categoria_id": 1}),
    ("post", f"{API}/proveedores/", {"nombre": "X"}),
    ("get", f"{API}/usuarios/", None),
    ("post", f"{API}/usuarios/", {"nombre": "X", "usuario": "xxx", "password": "una-clave-larga-123"}),
    ("get", f"{API}/compras/", None),
    ("post", f"{API}/compras/", {"proveedor_id": 1, "detalles": [{"producto_id": 1, "cantidad": 1, "costo_unitario": "1"}]}),
    ("post", f"{API}/movimientos-stock/", {"tipo": "MERMA", "observaciones": "prueba", "items": [{"producto_id": 1, "cantidad": 1}]}),
    ("post", f"{API}/ventas/1/anular", None),
]

# Rutas que exigen estar logueado (cualquier rol)
SOLO_LOGUEADO = [
    ("get", f"{API}/productos/"),
    ("get", f"{API}/categorias/"),
    ("get", f"{API}/clientes/"),
    ("get", f"{API}/ventas/"),
    ("get", f"{API}/usuarios/me"),
]


def _llamar(client, metodo, ruta, cuerpo, headers=None):
    kwargs = {"headers": headers}
    if cuerpo is not None:
        kwargs["json"] = cuerpo
    return client.request(metodo, ruta, **kwargs)


@pytest.mark.parametrize("metodo,ruta,cuerpo", SOLO_ADMIN)
def test_empleado_recibe_403_en_operaciones_de_admin(client, auth_empleado, metodo, ruta, cuerpo):
    assert _llamar(client, metodo, ruta, cuerpo, auth_empleado).status_code == 403


@pytest.mark.parametrize("metodo,ruta,cuerpo", SOLO_ADMIN)
def test_sin_token_recibe_401_en_operaciones_de_admin(client, metodo, ruta, cuerpo):
    assert _llamar(client, metodo, ruta, cuerpo).status_code == 401


@pytest.mark.parametrize("metodo,ruta", SOLO_LOGUEADO)
def test_sin_token_recibe_401_en_rutas_de_lectura(client, metodo, ruta):
    assert client.request(metodo, ruta).status_code == 401


@pytest.mark.parametrize("metodo,ruta", SOLO_LOGUEADO)
def test_empleado_puede_usar_rutas_de_lectura(client, auth_empleado, metodo, ruta):
    assert client.request(metodo, ruta, headers=auth_empleado).status_code == 200


def test_login_es_la_unica_ruta_publica(client):
    # Sin credenciales responde 422 (falta el formulario), NO 401: la ruta no exige token.
    assert client.post(f"{API}/auth/login").status_code == 422


def test_empleado_puede_vender(client, auth_empleado, crear_producto):
    pid = crear_producto(stock=5)
    r = client.post(
        f"{API}/ventas/",
        json={"detalles": [{"producto_id": pid, "cantidad": 1}]},
        headers=auth_empleado,
    )
    assert r.status_code == 201


def test_admin_puede_listar_usuarios(client, auth_admin):
    assert client.get(f"{API}/usuarios/", headers=auth_admin).status_code == 200
