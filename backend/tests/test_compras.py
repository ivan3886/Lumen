"""Compras a proveedores."""
from decimal import Decimal

from sqlalchemy import select

from app.enums import TipoMovimientoEnum
from app.models import Compra, MovimientoStock, MovimientoStockDetalle, Producto
from tests.helpers import dec

URL = "/api/v1/compras/"


def _body(proveedor_id, *items, **extra):
    return {
        "proveedor_id": proveedor_id,
        "detalles": [
            {"producto_id": pid, "cantidad": cant, "costo_unitario": costo} for pid, cant, costo in items
        ],
        **extra,
    }


def test_compra_suma_stock_exacto_actualiza_costo_y_calcula_total(
    client, db, auth_admin, admin, crear_producto, crear_proveedor, stock_de
):
    prov = crear_proveedor()
    p1 = crear_producto(stock=5, costo="600.00")
    p2 = crear_producto(stock=0, costo="50.00")

    r = client.post(URL, json=_body(prov, (p1, 10, "700.00"), (p2, 3, "100.55")), headers=auth_admin)

    assert r.status_code == 201
    compra = r.json()
    assert dec(compra["monto_total"]) == Decimal("7301.65")  # 10 x 700.00 + 3 x 100.55
    assert compra["usuario_id"] == admin.id
    assert stock_de(p1) == 15  # +10, NO +20 (regresión: antes el stock podía sumarse doble)
    assert stock_de(p2) == 3

    costo_nuevo = db.scalar(select(Producto.costo_actual).where(Producto.id == p1))
    assert costo_nuevo == Decimal("700.00")


def test_compra_genera_movimiento_de_stock(client, db, auth_admin, crear_producto, crear_proveedor):
    prov = crear_proveedor()
    pid = crear_producto(stock=5)
    compra_id = client.post(URL, json=_body(prov, (pid, 10, "700.00")), headers=auth_admin).json()["id"]

    mov = db.scalar(select(MovimientoStock).where(MovimientoStock.compra_id == compra_id))
    assert mov.tipo == TipoMovimientoEnum.COMPRA
    fila = db.execute(
        select(MovimientoStockDetalle.cantidad, MovimientoStockDetalle.stock_resultante).where(
            MovimientoStockDetalle.movimiento_id == mov.id
        )
    ).one()
    assert (fila.cantidad, fila.stock_resultante) == (10, 15)


def test_si_un_producto_no_existe_no_se_guarda_nada(client, auth_admin, crear_producto, crear_proveedor, stock_de, contar):
    prov = crear_proveedor()
    pid = crear_producto(stock=5)

    r = client.post(URL, json=_body(prov, (pid, 10, "700.00"), (9999, 1, "10.00")), headers=auth_admin)

    assert r.status_code == 404
    assert stock_de(pid) == 5
    assert contar(Compra) == 0
    assert contar(MovimientoStock) == 0


def test_proveedor_inactivo_o_inexistente_da_404(client, auth_admin, crear_producto, crear_proveedor):
    pid = crear_producto()
    inactivo = crear_proveedor(nombre="Inactivo", activo=False)
    assert client.post(URL, json=_body(inactivo, (pid, 1, "10.00")), headers=auth_admin).status_code == 404
    assert client.post(URL, json=_body(9999, (pid, 1, "10.00")), headers=auth_admin).status_code == 404


def test_producto_inactivo_no_se_puede_comprar(client, auth_admin, crear_producto, crear_proveedor, stock_de):
    prov = crear_proveedor()
    pid = crear_producto(stock=5, activo=False)
    assert client.post(URL, json=_body(prov, (pid, 1, "10.00")), headers=auth_admin).status_code == 404
    assert stock_de(pid) == 5


def test_compra_con_datos_invalidos_es_rechazada(client, auth_admin, crear_producto, crear_proveedor):
    prov = crear_proveedor()
    pid = crear_producto()
    assert client.post(URL, json={"proveedor_id": prov, "detalles": []}, headers=auth_admin).status_code == 422
    assert client.post(URL, json=_body(prov, (pid, 0, "10.00")), headers=auth_admin).status_code == 422
    assert client.post(URL, json=_body(prov, (pid, 1, "-5.00")), headers=auth_admin).status_code == 422
