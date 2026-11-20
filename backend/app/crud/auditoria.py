from typing import Optional

from sqlalchemy.orm import Session

from app.enums import AccionAuditoriaEnum
from app.models.auditoria import Auditoria


class CRUDAuditoria:
    def registrar(
        self,
        db: Session,
        *,
        usuario_id: int,
        tabla: str,
        registro_id: int,
        accion: AccionAuditoriaEnum,
        datos_anteriores: Optional[dict] = None,
        datos_nuevos: Optional[dict] = None,
        direccion_ip: Optional[str] = None,
    ) -> Auditoria:
        db_audit = Auditoria(
            usuario_id=usuario_id,
            tabla=tabla,
            registro_id=registro_id,
            accion=accion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            direccion_ip=direccion_ip,
        )
        db.add(db_audit)
        db.commit()
        db.refresh(db_audit)
        return db_audit


auditoria = CRUDAuditoria()
