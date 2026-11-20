"""Login, tokens y gestión de usuarios."""
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.enums import RolEnum
from tests.helpers import PASSWORD, bearer

LOGIN = "/api/v1/auth/login"
PROTEGIDO = "/api/v1/productos/"


def _token(sub, *, clave=None, algoritmo="HS256", minutos=60):
    ahora = datetime.now(timezone.utc)
    payload = {"sub": str(sub), "iat": ahora, "exp": ahora + timedelta(minutes=minutos)}
    return jwt.encode(payload, clave, algorithm=algoritmo)


CLAVE_REAL = lambda: settings.SECRET_KEY.get_secret_value()  # noqa: E731


# ---------------------------------------------------------------- login
def test_login_correcto_devuelve_token(client, admin):
    r = client.post(LOGIN, data={"username": "admin_test", "password": PASSWORD})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert r.json()["access_token"]


def test_login_con_contrasena_incorrecta_da_401(client, admin):
    r = client.post(LOGIN, data={"username": "admin_test", "password": "incorrecta-123456"})
    assert r.status_code == 401


def test_login_no_revela_si_el_usuario_existe(client, admin):
    """Usuario inexistente y contraseña mala deben ser indistinguibles (evita enumeración de usuarios)."""
    mala = client.post(LOGIN, data={"username": "admin_test", "password": "incorrecta-123456"})
    inexistente = client.post(LOGIN, data={"username": "no_existe", "password": "incorrecta-123456"})
    assert mala.status_code == inexistente.status_code == 401
    assert mala.json() == inexistente.json()


def test_login_de_usuario_inactivo_da_401(client, nuevo_usuario):
    nuevo_usuario("inactivo", RolEnum.EMPLEADO, activo=False)
    r = client.post(LOGIN, data={"username": "inactivo", "password": PASSWORD})
    assert r.status_code == 401


# ---------------------------------------------------------------- tokens
def test_sin_token_da_401(client):
    assert client.get(PROTEGIDO).status_code == 401


def test_token_basura_da_401(client):
    assert client.get(PROTEGIDO, headers=bearer("esto-no-es-un-jwt")).status_code == 401


def test_token_expirado_da_401(client, admin):
    token = _token(admin.id, clave=CLAVE_REAL(), minutos=-5)
    assert client.get(PROTEGIDO, headers=bearer(token)).status_code == 401


def test_token_firmado_con_otra_clave_da_401(client, admin):
    token = _token(admin.id, clave="otra-clave-" + "y" * 40)
    assert client.get(PROTEGIDO, headers=bearer(token)).status_code == 401


def test_token_con_algoritmo_none_es_rechazado(client, admin):
    """Ataque clásico: un token sin firma ('alg: none'). El servidor solo acepta HS256."""
    token = _token(admin.id, clave=None, algoritmo="none")
    assert client.get(PROTEGIDO, headers=bearer(token)).status_code == 401


def test_token_de_usuario_inexistente_da_401(client, admin):
    token = _token(99999, clave=CLAVE_REAL())
    assert client.get(PROTEGIDO, headers=bearer(token)).status_code == 401


def test_desactivar_usuario_invalida_su_token_al_instante(client, db, empleado, login):
    token = login("empleado_test").json()["access_token"]
    assert client.get("/api/v1/usuarios/me", headers=bearer(token)).status_code == 200

    empleado.activo = False
    db.commit()

    assert client.get("/api/v1/usuarios/me", headers=bearer(token)).status_code == 401


def test_me_no_expone_la_contrasena(client, auth_empleado):
    r = client.get("/api/v1/usuarios/me", headers=auth_empleado)
    assert r.status_code == 200
    assert "password" not in r.json()
    assert "password_hash" not in r.json()
    assert r.json()["rol"] == "empleado"


# ---------------------------------------------------------------- alta de usuarios
def _nuevo(**cambios):
    datos = {"nombre": "Ana", "usuario": "ana", "password": "una-clave-larga-123"}
    datos.update(cambios)
    return datos


def test_admin_crea_usuario_y_este_puede_loguearse(client, auth_admin, login):
    r = client.post("/api/v1/usuarios/", json=_nuevo(), headers=auth_admin)
    assert r.status_code == 201
    assert r.json()["rol"] == "empleado"  # por defecto NO es admin
    assert login("ana", "una-clave-larga-123").status_code == 200


def test_contrasena_corta_es_rechazada(client, auth_admin):
    r = client.post("/api/v1/usuarios/", json=_nuevo(password="corta"), headers=auth_admin)
    assert r.status_code == 422


def test_contrasena_de_mas_de_72_bytes_es_rechazada(client, auth_admin):
    # 'á' ocupa 2 bytes: 37 caracteres = 74 bytes, por encima del límite de bcrypt
    r = client.post("/api/v1/usuarios/", json=_nuevo(password="á" * 37), headers=auth_admin)
    assert r.status_code == 422


def test_rol_invalido_es_rechazado(client, auth_admin):
    r = client.post("/api/v1/usuarios/", json=_nuevo(rol="superadmin"), headers=auth_admin)
    assert r.status_code == 422


def test_usuario_duplicado_da_409(client, auth_admin):
    assert client.post("/api/v1/usuarios/", json=_nuevo(), headers=auth_admin).status_code == 201
    assert client.post("/api/v1/usuarios/", json=_nuevo(), headers=auth_admin).status_code == 409
