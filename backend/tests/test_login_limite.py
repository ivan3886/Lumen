"""Límite de intentos de login (protección contra fuerza bruta)."""
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.clock import ahora_utc
from app.core.config import settings
from app.main import app
from app.models import IntentoLogin
from tests.helpers import PASSWORD

LOGIN = "/api/v1/auth/login"
MAL = "incorrecta-123456"


def _intentar(client, usuario="admin_test", password=MAL):
    return client.post(LOGIN, data={"username": usuario, "password": password})


def _fallar(client, veces, usuario="admin_test"):
    codigos = [_intentar(client, usuario).status_code for _ in range(veces)]
    assert codigos == [401] * veces  # mientras no se llegue al límite, solo es "credenciales incorrectas"


def _intento_viejo(db, usuario, *, minutos_atras, exitoso=False, ip="testclient"):
    """Inserta un intento con fecha pasada: simula que el tiempo transcurrió sin esperar."""
    db.add(
        IntentoLogin(
            usuario=usuario,
            direccion_ip=ip,
            exitoso=exitoso,
            fecha=ahora_utc() - timedelta(minutes=minutos_atras),
        )
    )
    db.commit()


# ---------------------------------------------------------------- bloqueo básico
def test_cinco_fallos_bloquean_el_sexto_intento_incluso_con_la_clave_correcta(client, admin):
    _fallar(client, 5)

    r = _intentar(client, password=PASSWORD)  # ¡la contraseña CORRECTA!

    assert r.status_code == 429
    assert int(r.headers["Retry-After"]) > 0


def test_menos_fallos_que_el_limite_no_bloquean(client, admin):
    _fallar(client, 4)
    assert _intentar(client, password=PASSWORD).status_code == 200


def test_un_login_exitoso_reinicia_el_contador(client, admin):
    _fallar(client, 4)
    assert _intentar(client, password=PASSWORD).status_code == 200

    _fallar(client, 4)  # otros 4 fallos: sin el reinicio ya estaría bloqueado
    assert _intentar(client, password=PASSWORD).status_code == 200


def test_el_bloqueo_de_un_usuario_no_afecta_a_otro(client, admin, empleado):
    _fallar(client, 5, usuario="admin_test")
    assert _intentar(client, "admin_test", PASSWORD).status_code == 429
    assert _intentar(client, "empleado_test", PASSWORD).status_code == 200


# ---------------------------------------------------------------- seguridad
def test_usuario_inexistente_se_bloquea_igual_que_uno_real(client, admin):
    """Si solo las cuentas reales se bloquearan, el bloqueo delataría qué usuarios existen."""
    _fallar(client, 5, usuario="admin_test")
    _fallar(client, 5, usuario="fantasma")

    real = _intentar(client, "admin_test")
    falso = _intentar(client, "fantasma")

    assert real.status_code == falso.status_code == 429
    assert real.json() == falso.json()


def test_rociado_de_contrasenas_bloquea_la_ip(client, admin, monkeypatch):
    """Password spraying: una misma clave probada en muchas cuentas evita el límite por usuario,
    pero no el límite por IP."""
    monkeypatch.setattr(settings, "LOGIN_MAX_INTENTOS_IP", 6)
    for i in range(6):
        assert _intentar(client, usuario=f"cuenta{i}").status_code == 401  # 1 solo fallo por cuenta

    assert _intentar(client, "admin_test", PASSWORD).status_code == 429  # ni siquiera una cuenta válida


def test_usuario_gigante_no_rompe_el_login(client):
    assert _intentar(client, usuario="a" * 300).status_code == 401


# ---------------------------------------------------------------- tiempo
def test_los_fallos_viejos_ya_no_cuentan(client, db, admin):
    for _ in range(5):
        _intento_viejo(db, "admin_test", minutos_atras=settings.LOGIN_VENTANA_MINUTOS + 1)

    assert _intentar(client, password=PASSWORD).status_code == 200


def test_el_tiempo_de_espera_se_calcula_bien(client, db, admin):
    # 5 fallos de hace 14 minutos con una ventana de 15: faltan ~60 segundos
    for _ in range(5):
        _intento_viejo(db, "admin_test", minutos_atras=settings.LOGIN_VENTANA_MINUTOS - 1)

    r = _intentar(client, password=PASSWORD)

    assert r.status_code == 429
    assert 1 <= int(r.headers["Retry-After"]) <= 60


def test_los_intentos_durante_el_bloqueo_no_lo_alargan(client, db, admin):
    _fallar(client, 5)
    for _ in range(3):
        assert _intentar(client).status_code == 429

    cantidad = len(db.scalars(select(IntentoLogin).where(IntentoLogin.usuario == "admin_test")).all())
    assert cantidad == 5  # los 3 intentos bloqueados no se anotaron


# ---------------------------------------------------------------- registro
def test_se_registran_intentos_fallidos_y_exitosos(client, db, admin):
    _fallar(client, 1)
    assert _intentar(client, password=PASSWORD).status_code == 200

    filas = db.execute(
        select(IntentoLogin.usuario, IntentoLogin.exitoso, IntentoLogin.direccion_ip).order_by(IntentoLogin.id)
    ).all()
    assert [(f.usuario, f.exitoso) for f in filas] == [("admin_test", False), ("admin_test", True)]
    assert filas[0].direccion_ip == "testclient"


def test_se_purgan_los_registros_de_mas_de_30_dias(client, db, admin):
    _intento_viejo(db, "alguien", minutos_atras=31 * 24 * 60)
    assert _intentar(client, password=PASSWORD).status_code == 200  # el login exitoso dispara la limpieza

    assert db.scalar(select(IntentoLogin.id).where(IntentoLogin.usuario == "alguien")) is None


# ---------------------------------------------------------------- concurrencia
def test_una_rafaga_en_paralelo_no_permite_mas_intentos_que_el_limite(admin):
    """12 pedidos simultáneos con contraseña mala: como MÁXIMO 5 pueden llegar a probarla.

    Un 401 significa "se probó la contraseña y era incorrecta"; un 429, "bloqueado antes
    de probarla". Es el motivo de registrar el intento ANTES de verificar la contraseña."""
    barrera = threading.Barrier(12)

    def atacar() -> int:
        with TestClient(app) as cliente:
            barrera.wait(timeout=10)
            return _intentar(cliente).status_code

    with ThreadPoolExecutor(max_workers=12) as pool:
        codigos = [f.result() for f in [pool.submit(atacar) for _ in range(12)]]

    assert set(codigos) <= {401, 429}  # ningún error 500 inesperado
    assert codigos.count(401) <= settings.LOGIN_MAX_INTENTOS_USUARIO
    assert codigos.count(401) + codigos.count(429) == 12