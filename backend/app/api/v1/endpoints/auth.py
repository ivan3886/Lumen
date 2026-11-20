import logging
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.security import create_access_token
from app.crud.intento_login import intento_login as crud_intento
from app.crud.usuario import usuario as crud_usuario
from app.schemas.token import Token

logger = logging.getLogger("lumen.auth")
router = APIRouter()

MAX_LARGO_USUARIO = 50  # igual que la columna usuario.usuario


def _demasiados_intentos(segundos: int) -> HTTPException:
    minutos = ceil(segundos / 60)
    return HTTPException(
        status_code=429,
        detail=f"Demasiados intentos fallidos. Intentá de nuevo en {minutos} minuto(s).",
        headers={"Retry-After": str(segundos)},
    )


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session),
):
    ip = request.client.host if request.client else "desconocida"
    usuario = form.username[:MAX_LARGO_USUARIO]  # recortado: un atacante podría mandar textos enormes

    # 1) ¿Ya está bloqueado? Se responde SIN registrar el intento ni mirar la contraseña:
    #    así los intentos durante el bloqueo no lo alargan, y acertar la clave no sirve de nada.
    espera = crud_intento.segundos_de_espera(db, usuario=usuario, ip=ip)
    if espera:
        logger.warning("Login bloqueado: usuario=%r ip=%s", usuario, ip)  # %r: evita inyección de líneas en el log
        raise _demasiados_intentos(espera)

    # 2) Se registra el intento ANTES de verificar la contraseña y se vuelve a contar.
    #    Si se registrara después, 50 pedidos en paralelo pasarían el control 1 a la vez
    #    y cada uno probaría una contraseña antes de que se anote el primer fallo.
    intento = crud_intento.registrar_intento(db, usuario=usuario, ip=ip)
    espera = crud_intento.segundos_de_espera(db, usuario=usuario, ip=ip, extra=1)
    if espera:
        logger.warning("Login bloqueado (ráfaga): usuario=%r ip=%s", usuario, ip)
        raise _demasiados_intentos(espera)

    # 3) Recién ahora se verifica la contraseña.
    user = crud_usuario.authenticate(db, usuario=form.username, password=form.password)
    if user is None:
        # Mismo mensaje para "usuario inexistente", "contraseña mala" y "usuario inactivo".
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    crud_intento.marcar_exitoso(db, intento)
    crud_intento.purgar_antiguos(db)
    return Token(access_token=create_access_token(user.id))
