from datetime import datetime, timedelta
from math import ceil
from typing import List, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.clock import ahora_utc
from app.core.config import settings
from app.models.intento_login import IntentoLogin


class CRUDIntentoLogin:
    def _fechas_de_fallos(
        self, db: Session, *, usuario: Optional[str] = None, ip: Optional[str] = None
    ) -> List[datetime]:
        """Fechas (de la más vieja a la más nueva) de los fallos dentro de la ventana."""
        desde = ahora_utc() - timedelta(minutes=settings.LOGIN_VENTANA_MINUTOS)
        condiciones = [IntentoLogin.exitoso.is_(False), IntentoLogin.fecha > desde]

        if usuario is not None:
            condiciones.append(IntentoLogin.usuario == usuario)
            # Un login exitoso "borra la cuenta": solo cuentan los fallos posteriores a él.
            ultimo_exito = db.scalar(
                select(func.max(IntentoLogin.fecha)).where(
                    IntentoLogin.usuario == usuario, IntentoLogin.exitoso.is_(True)
                )
            )
            if ultimo_exito is not None:
                condiciones.append(IntentoLogin.fecha > ultimo_exito)

        if ip is not None:
            # Por IP NO se reinicia con un éxito: así un atacante no se "limpia" entrando a su propia cuenta.
            condiciones.append(IntentoLogin.direccion_ip == ip)

        return list(db.scalars(select(IntentoLogin.fecha).where(*condiciones).order_by(IntentoLogin.fecha)))

    @staticmethod
    def _espera(fechas: List[datetime], maximo: int) -> int:
        """0 si no hay bloqueo; si lo hay, segundos hasta que un fallo viejo salga de la ventana."""
        if len(fechas) < maximo:
            return 0
        # Se desbloquea cuando la cantidad de fallos baja de 'maximo': eso pasa al vencer este fallo.
        vence = fechas[len(fechas) - maximo] + timedelta(minutes=settings.LOGIN_VENTANA_MINUTOS)
        return max(1, ceil((vence - ahora_utc()).total_seconds()))

    def segundos_de_espera(self, db: Session, *, usuario: str, ip: str, extra: int = 0) -> int:
        por_usuario = self._espera(
            self._fechas_de_fallos(db, usuario=usuario), settings.LOGIN_MAX_INTENTOS_USUARIO + extra
        )
        por_ip = self._espera(self._fechas_de_fallos(db, ip=ip), settings.LOGIN_MAX_INTENTOS_IP + extra)
        return max(por_usuario, por_ip)

    def registrar_intento(self, db: Session, *, usuario: str, ip: str) -> IntentoLogin:
        """Guarda el intento como FALLIDO. Si la contraseña resulta correcta, se marca como exitoso."""
        intento = IntentoLogin(usuario=usuario, direccion_ip=ip, exitoso=False)
        db.add(intento)
        db.commit()
        db.refresh(intento)
        return intento

    def marcar_exitoso(self, db: Session, intento: IntentoLogin) -> None:
        intento.exitoso = True
        db.commit()

    def purgar_antiguos(self, db: Session, *, dias: int = 30) -> None:
        """Evita que la tabla crezca sin límite (un atacante podría llenarla de intentos)."""
        db.execute(delete(IntentoLogin).where(IntentoLogin.fecha < ahora_utc() - timedelta(days=dias)))
        db.commit()


intento_login = CRUDIntentoLogin()
