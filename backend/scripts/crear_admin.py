"""Crea el primer usuario administrador.

Uso (desde la carpeta backend/, con el venv activado):
    python -m scripts.crear_admin

Hace falta porque POST /usuarios exige ser admin: sin ningún admin, nadie podría crear usuarios.
"""
import getpass
import sys

from pydantic import ValidationError

from app.crud.usuario import usuario as crud_usuario
from app.db.database import SessionLocal
from app.enums import RolEnum
from app.schemas.usuario import UsuarioCreate


def main() -> None:
    nombre = input("Nombre completo: ").strip()
    usuario = input("Nombre de usuario: ").strip()
    password = getpass.getpass("Contraseña (mínimo 10 caracteres): ")
    if password != getpass.getpass("Repetir contraseña: "):
        sys.exit("Las contraseñas no coinciden.")

    try:
        datos = UsuarioCreate(nombre=nombre, usuario=usuario, password=password, rol=RolEnum.ADMIN)
    except ValidationError as e:
        sys.exit(f"Datos inválidos:\n{e}")

    with SessionLocal() as db:
        if crud_usuario.get_by_usuario(db, usuario):
            sys.exit("Ese nombre de usuario ya existe.")
        crud_usuario.create(db, obj_in=datos)
    print("Administrador creado correctamente.")


if __name__ == "__main__":
    main()
