"""Catálogo de productos."""
from decimal import Decimal

from tests.helpers import dec

API = "/api/v1"


def _categoria(client, headers) -> int:
    r = client.post(f"{API}/categorias/", json={"nombre": "Biblias"}, headers=headers)
    assert r.status_code == 201
    return r.json()["id"]


def _producto(categoria_id, **cambios):
    datos = {
        "codigo_interno": "LIB-001",
        "codigo_barras": "9789871234567",
        "titulo": "Biblia de Jerusalén",
        "categoria_id": categoria_id,
        "costo_actual": "5000.00",
        "precio_venta": "8000.00",
    }
    datos.update(cambios)
    return datos


def test_crear_producto_arranca_con_stock_cero(client, auth_admin):
    cat = _categoria(client, auth_admin)
    r = client.post(f"{API}/productos/", json=_producto(cat), headers=auth_admin)
    assert r.status_code == 201
    assert r.json()["stock_actual"] == 0


def test_no_se_puede_fijar_el_stock_al_crear(client, auth_admin):
    """El stock solo cambia por compras, ventas o ajustes: un campo 'stock_actual' se ignora."""
    cat = _categoria(client, auth_admin)
    r = client.post(f"{API}/productos/", json=_producto(cat, stock_actual=999), headers=auth_admin)
    assert r.status_code == 201
    assert r.json()["stock_actual"] == 0


def test_codigo_interno_duplicado_da_409(client, auth_admin):
    cat = _categoria(client, auth_admin)
    assert client.post(f"{API}/productos/", json=_producto(cat), headers=auth_admin).status_code == 201
    r = client.post(f"{API}/productos/", json=_producto(cat, codigo_barras="9780000000001"), headers=auth_admin)
    assert r.status_code == 409


def test_codigo_de_barras_duplicado_da_409(client, auth_admin):
    cat = _categoria(client, auth_admin)
    assert client.post(f"{API}/productos/", json=_producto(cat), headers=auth_admin).status_code == 201
    r = client.post(f"{API}/productos/", json=_producto(cat, codigo_interno="LIB-002"), headers=auth_admin)
    assert r.status_code == 409


def test_precio_negativo_es_rechazado(client, auth_admin):
    cat = _categoria(client, auth_admin)
    r = client.post(f"{API}/productos/", json=_producto(cat, precio_venta="-1"), headers=auth_admin)
    assert r.status_code == 422


def test_categoria_inexistente_da_409_sin_filtrar_detalles_internos(client, auth_admin):
    r = client.post(f"{API}/productos/", json=_producto(9999), headers=auth_admin)
    assert r.status_code == 409
    texto = r.text.lower()
    assert "foreign key" not in texto and "violates" not in texto and "producto_" not in texto


def test_patch_cambia_el_precio_pero_ignora_el_stock(client, auth_admin, crear_producto, stock_de):
    pid = crear_producto(stock=4)
    r = client.patch(
        f"{API}/productos/{pid}",
        json={"precio_venta": "1500.00", "stock_actual": 999},
        headers=auth_admin,
    )
    assert r.status_code == 200
    assert dec(r.json()["precio_venta"]) == Decimal("1500.00")
    assert stock_de(pid) == 4


def test_desactivar_producto_con_patch(client, auth_admin, crear_producto):
    pid = crear_producto()
    r = client.patch(f"{API}/productos/{pid}", json={"activo": False}, headers=auth_admin)
    assert r.status_code == 200
    assert r.json()["activo"] is False


def test_patch_de_producto_inexistente_da_404(client, auth_admin):
    assert client.patch(f"{API}/productos/9999", json={"titulo": "X"}, headers=auth_admin).status_code == 404


def test_limite_de_paginacion_tiene_tope(client, auth_empleado):
    assert client.get(f"{API}/productos/?limit=501", headers=auth_empleado).status_code == 422
    assert client.get(f"{API}/productos/?limit=0", headers=auth_empleado).status_code == 422
    assert client.get(f"{API}/productos/?skip=-1", headers=auth_empleado).status_code == 422
    assert client.get(f"{API}/productos/?limit=500", headers=auth_empleado).status_code == 200
