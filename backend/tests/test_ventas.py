"""Ventas: precios, stock, atomicidad, anulación y concurrencia."""
import threading
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.enums import EstadoVentaEnum, TipoMovimientoEnum
from app.main import app
from app.models import (
    Cliente,
    MovimientoStock,
    MovimientoStockDetalle,
    Remito,
    Venta,
)
from tests.helpers import dec

URL = "/api/v1/ventas/"


def _body(*items, **extra):
    return {"detalles": [{"producto_id": pid, "cantidad": cant} for pid, cant in items], **extra}


# ------------------------------------------------------------------ venta correcta
def test_venta_correcta_calcula_total_descuenta_stock_y_genera_remito(
    client, db, auth_empleado, empleado, crear_producto, stock_de
):
    pid = crear_producto(stock=10, precio="1250.50", costo="600.00")

    r = client.post(URL, json=_body((pid, 2)), headers=auth_empleado)

    assert r.status_code == 201
    venta = r.json()
    assert dec(venta["monto_total"]) == Decimal("2501.00")  # 2 x 1250.50
    assert venta["usuario_id"] == empleado.id  # sale del token
    assert venta["estado"] == "COMPLETADA"
    assert venta["remito"]["numero_remito"] == "REM-0000001"
    assert stock_de(pid) == 8

    detalle = venta["detalles"][0]
    assert dec(detalle["precio_unitario"]) == Decimal("1250.50")
    assert dec(detalle["costo_historico"]) == Decimal("600.00")  # para calcular márgenes a futuro
    assert dec(detalle["subtotal"]) == Decimal("2501.00")


def test_sin_cliente_usa_consumidor_final(client, db, auth_empleado, crear_producto):
    pid = crear_producto()
    consumidor_final = db.scalar(select(Cliente.id).where(Cliente.nombre == "CONSUMIDOR FINAL"))
    r = client.post(URL, json=_body((pid, 1)), headers=auth_empleado)
    assert r.json()["cliente_id"] == consumidor_final


def test_el_precio_lo_define_el_servidor_no_el_cliente(client, auth_empleado, crear_producto):
    """Aunque el cliente mande un precio falso en el JSON, se usa el de la base."""
    pid = crear_producto(precio="1000.00")
    cuerpo = {"detalles": [{"producto_id": pid, "cantidad": 1, "precio_unitario": "1.00"}]}
    r = client.post(URL, json=cuerpo, headers=auth_empleado)
    assert r.status_code == 201
    assert dec(r.json()["monto_total"]) == Decimal("1000.00")


def test_la_venta_registra_un_movimiento_de_stock(client, db, auth_empleado, crear_producto):
    pid = crear_producto(stock=10)
    venta_id = client.post(URL, json=_body((pid, 3)), headers=auth_empleado).json()["id"]

    mov = db.scalar(select(MovimientoStock).where(MovimientoStock.venta_id == venta_id))
    assert mov.tipo == TipoMovimientoEnum.VENTA
    fila = db.execute(
        select(MovimientoStockDetalle.cantidad, MovimientoStockDetalle.stock_resultante).where(
            MovimientoStockDetalle.movimiento_id == mov.id
        )
    ).one()
    assert fila.cantidad == -3
    assert fila.stock_resultante == 7


# ------------------------------------------------------------------ stock y atomicidad
def test_stock_insuficiente_da_409_y_no_deja_rastros(client, auth_empleado, crear_producto, stock_de, contar):
    pid = crear_producto(stock=2)

    r = client.post(URL, json=_body((pid, 3)), headers=auth_empleado)

    assert r.status_code == 409
    assert stock_de(pid) == 2
    assert contar(Venta) == 0 and contar(Remito) == 0 and contar(MovimientoStock) == 0


def test_si_falla_un_producto_no_se_descuenta_ninguno(client, auth_empleado, crear_producto, stock_de, contar):
    """Atomicidad: 'todo o nada'. El primer libro alcanzaba, el segundo no: nada debe cambiar."""
    p1 = crear_producto(stock=10)
    p2 = crear_producto(stock=1)

    r = client.post(URL, json=_body((p1, 2), (p2, 5)), headers=auth_empleado)

    assert r.status_code == 409
    assert stock_de(p1) == 10
    assert stock_de(p2) == 1
    assert contar(Venta) == 0


def test_mismo_libro_en_dos_lineas_se_suma(client, auth_empleado, crear_producto, stock_de):
    pid = crear_producto(stock=5)

    # 3 + 3 = 6 > 5: debe rechazarse (antes cada línea se validaba por separado)
    assert client.post(URL, json=_body((pid, 3), (pid, 3)), headers=auth_empleado).status_code == 409
    assert stock_de(pid) == 5

    # 2 + 3 = 5: alcanza, y se guarda UNA sola línea con cantidad 5
    r = client.post(URL, json=_body((pid, 2), (pid, 3)), headers=auth_empleado)
    assert r.status_code == 201
    assert len(r.json()["detalles"]) == 1
    assert r.json()["detalles"][0]["cantidad"] == 5
    assert stock_de(pid) == 0


def test_producto_inactivo_no_se_puede_vender(client, auth_empleado, crear_producto, stock_de):
    pid = crear_producto(stock=5, activo=False)
    assert client.post(URL, json=_body((pid, 1)), headers=auth_empleado).status_code == 404
    assert stock_de(pid) == 5


def test_producto_inexistente_da_404(client, auth_empleado):
    assert client.post(URL, json=_body((9999, 1)), headers=auth_empleado).status_code == 404


def test_cliente_inactivo_o_inexistente_da_404(client, db, auth_empleado, crear_producto):
    pid = crear_producto()
    inactivo = Cliente(nombre="Cliente Inactivo", activo=False)
    db.add(inactivo)
    db.commit()

    assert client.post(URL, json=_body((pid, 1), cliente_id=inactivo.id), headers=auth_empleado).status_code == 404
    assert client.post(URL, json=_body((pid, 1), cliente_id=9999), headers=auth_empleado).status_code == 404


# ------------------------------------------------------------------ validación de entrada
def test_venta_sin_productos_es_rechazada(client, auth_empleado):
    assert client.post(URL, json={"detalles": []}, headers=auth_empleado).status_code == 422


def test_cantidades_cero_o_negativas_son_rechazadas(client, auth_empleado, crear_producto):
    pid = crear_producto()
    assert client.post(URL, json=_body((pid, 0)), headers=auth_empleado).status_code == 422
    assert client.post(URL, json=_body((pid, -2)), headers=auth_empleado).status_code == 422


def test_medio_de_pago_invalido_es_rechazado(client, auth_empleado, crear_producto):
    pid = crear_producto()
    assert client.post(URL, json=_body((pid, 1), medio_pago="BITCOIN"), headers=auth_empleado).status_code == 422


# ------------------------------------------------------------------ anulación
def test_anular_venta_devuelve_el_stock(client, db, auth_admin, auth_empleado, crear_producto, stock_de):
    pid = crear_producto(stock=10)
    venta_id = client.post(URL, json=_body((pid, 3)), headers=auth_empleado).json()["id"]
    assert stock_de(pid) == 7

    r = client.post(f"{URL}{venta_id}/anular", headers=auth_admin)

    assert r.status_code == 200
    assert r.json()["estado"] == EstadoVentaEnum.ANULADA.value
    assert stock_de(pid) == 10

    devolucion = db.scalar(
        select(MovimientoStock).where(
            MovimientoStock.venta_id == venta_id,
            MovimientoStock.tipo == TipoMovimientoEnum.DEVOLUCION_CLIENTE,
        )
    )
    assert devolucion is not None


def test_anular_dos_veces_da_409_y_no_duplica_el_stock(client, auth_admin, auth_empleado, crear_producto, stock_de):
    pid = crear_producto(stock=10)
    venta_id = client.post(URL, json=_body((pid, 3)), headers=auth_empleado).json()["id"]

    assert client.post(f"{URL}{venta_id}/anular", headers=auth_admin).status_code == 200
    assert client.post(f"{URL}{venta_id}/anular", headers=auth_admin).status_code == 409
    assert stock_de(pid) == 10  # no 13


def test_anular_venta_inexistente_da_404(client, auth_admin):
    assert client.post(f"{URL}9999/anular", headers=auth_admin).status_code == 404


# ------------------------------------------------------------------ concurrencia
def test_dos_ventas_simultaneas_del_ultimo_ejemplar_no_venden_de_mas(
    auth_empleado, crear_producto, stock_de, contar
):
    """Prueba del bloqueo de filas (SELECT ... FOR UPDATE).

    Dos cajas venden el ÚNICO ejemplar al mismo tiempo. Debe haber exactamente una venta
    exitosa y un rechazo. Si se quita .with_for_update() del código, este test puede
    empezar a fallar (es una condición de carrera, no siempre ocurre).
    """
    pid = crear_producto(stock=1)
    barrera = threading.Barrier(2)  # hace que ambos hilos disparen a la vez

    def vender() -> int:
        with TestClient(app) as cliente:
            barrera.wait(timeout=10)
            return cliente.post(URL, json=_body((pid, 1)), headers=auth_empleado).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        futuros = [pool.submit(vender) for _ in range(2)]
        resultados = sorted(f.result() for f in futuros)

    assert resultados == [201, 409]
    assert stock_de(pid) == 0
    assert contar(Venta) == 1
