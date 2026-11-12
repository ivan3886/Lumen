from enum import Enum

class TipoMovimientoEnum(str, Enum):
    COMPRA = "COMPRA"
    VENTA = "VENTA"
    MERMA = "MERMA"
    PERDIDA = "PERDIDA"
    AJUSTE_POSITIVO = "AJUSTE_POSITIVO"
    AJUSTE_NEGATIVO = "AJUSTE_NEGATIVO"
    DEVOLUCION_CLIENTE = "DEVOLUCION_CLIENTE"
    DEVOLUCION_PROVEEDOR = "DEVOLUCION_PROVEEDOR"

class MedioPagoEnum(str, Enum):
    EFECTIVO = "EFECTIVO"
    TRANSFERENCIA = "TRANSFERENCIA"
    TARJETA = "TARJETA"
    OTRO = "OTRO"

class EstadoVentaEnum(str, Enum):
    COMPLETADA = "COMPLETADA"
    ANULADA = "ANULADA"

class AccionAuditoriaEnum(str, Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"