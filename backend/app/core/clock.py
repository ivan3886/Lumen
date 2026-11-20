from datetime import datetime, timezone


def ahora_utc() -> datetime:
    """Hora actual en UTC, sin zona horaria (naive).

    Las columnas TIMESTAMP de la base no guardan zona; usar SIEMPRE UTC evita errores
    por cambios de horario (verano/invierno) o por servidores en otra zona.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
