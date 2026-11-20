from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.security import create_access_token
from app.crud.usuario import usuario as crud_usuario
from app.schemas.token import Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    user = crud_usuario.authenticate(db, usuario=form.username, password=form.password)
    if user is None:
        # Mismo mensaje para "usuario inexistente", "contraseña mala" y "usuario inactivo".
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))
