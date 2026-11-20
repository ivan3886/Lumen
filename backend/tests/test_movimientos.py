"""Ajustes manuales de stock (mermas, pérdidas, ajustes)."""
from sqlalchemy import select

from app.models import MovimientoStock, MovimientoStockDetalle

URL = "/api/v1/movimientos-stock/"


def _body(tipo, *items, observaciones="Ajuste de prueba"):
    cuerpo = {"tipo": tipo, "items": [{"producto_id": pid, "cantidad": cant} for pid, cant in items]}
    if observaciones is not None:
        cuerpo["observaciones"] = observaciones
    return cuerpo


def test_merma_baja_el_stock_y_queda_registrada(client, db, auth_admin, crear_producto, stock_de):
    pid = crear_producto(stock=10)

    r = client.post(URL, json=_body("MERMA", (pid, 3)), headers=auth_admin)

    assert r.status_code == 201
    assert r.json()["tipo"] == "MERMA"
    assert r.json()["detalles"][0]["cantidad"] == -3  # el sistema pone el signo según el tipo
    assert r.json()["detalles"][0]["stock_resultante"] == 7
    assert stock_de(pid) == 7


def test_ajuste_positivo_sube_el_stock(client, auth_admin, crear_producto, stock_de):
    pid = crear_producto(stock=10)
    assert client.post(URL, json=_body("AJUSTE_POSITIVO", (pid, 5)), headers=auth_admin).status_code == 201
    assert stock_de(pid) == 15


def test_merma_mayor_al_stock_da_409_y_no_cambia_nada(client, auth_admin, crear_producto, stock_de, contar):
    pid = crear_producto(stock=2)
    r = client.post(URL, json=_body("MERMA", (pid, 5)), headers=auth_admin)
    assert r.status_code == 409
    assert stock_de(pid) == 2
    assert contar(MovimientoStock) == 0


def test_mismo_producto_repetido_se_acumula(client, auth_admin, crear_producto, stock_de):
    pid = crear_producto(stock=5)
    assert client.post(URL, json=_body("MERMA", (pid, 3), (pid, 3)), headers=auth_admin).status_code == 409
    assert stock_de(pid) == 5


def test_no_se_pueden_cargar_a_mano_movimientos_de_venta_ni_compra(client, auth_admin, crear_producto):
    pid = crear_producto()
    assert client.post(URL, json=_body("VENTA", (pid, 1)), headers=auth_admin).status_code == 422
    assert client.post(URL, json=_body("COMPRA", (pid, 1)), headers=auth_admin).status_code == 422


def test_cantidad_cero_o_negativa_es_rechazada(client, auth_admin, crear_producto, stock_de):
    """Regresión del bug de signo: una merma con cantidad negativa antes SUMABA stock."""
    pid = crear_producto(stock=10)
    assert client.post(URL, json=_body("MERMA", (pid, 0)), headers=auth_admin).status_code == 422
    assert client.post(URL, json=_body("MERMA", (pid, -5)), headers=auth_admin).status_code == 422
    assert stock_de(pid) == 10


def test_el_motivo_es_obligatorio(client, auth_admin, crear_producto):
    pid = crear_producto()
    assert client.post(URL, json=_body("MERMA", (pid, 1), observaciones=None), headers=auth_admin).status_code == 422
    assert client.post(URL, json=_body("MERMA", (pid, 1), observaciones="x"), headers=auth_admin).status_code == 422


def test_producto_inexistente_da_404(client, auth_admin):
    assert client.post(URL, json=_body("MERMA", (9999, 1)), headers=auth_admin).status_code == 404
