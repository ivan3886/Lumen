CREATE TYPE tipo_movimiento AS ENUM (
    'COMPRA',
    'VENTA',
    'MERMA',
    'PERDIDA',
    'AJUSTE_POSITIVO',
    'AJUSTE_NEGATIVO',
    'DEVOLUCION_CLIENTE',
    'DEVOLUCION_PROVEEDOR'
);

CREATE TYPE medio_pago AS ENUM (
    'EFECTIVO',
    'TRANSFERENCIA',
    'TARJETA',
    'OTRO'
);

CREATE TYPE estado_venta AS ENUM (
    'COMPLETADA',
    'ANULADA'
);

CREATE TYPE accion_auditoria AS ENUM (
    'INSERT',
    'UPDATE',
    'DELETE'
);