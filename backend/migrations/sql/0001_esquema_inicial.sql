-- MIGRACIÓN 0001: esquema inicial de Lumen (copia CONGELADA de types.sql + schema.sql + seed.sql).
-- No editar este archivo: los cambios futuros van en migraciones nuevas.

-- ===================== types.sql =====================
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
-- ===================== schema.sql ====================
-- Esquema principal de tablas para Lumen
-- ORDEN DE EJECUCIÓN: primero types.sql, después este archivo y por último seed.sql.

-- 1. Usuarios del sistema
CREATE TABLE usuario (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'empleado',
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_usuario_rol CHECK (rol IN ('admin', 'empleado'))
);

-- 2. Clientes (Consumidor Final se insertará en seed.sql)
CREATE TABLE cliente (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    cuit VARCHAR(20),
    direccion VARCHAR(150),
    telefono VARCHAR(30),
    email VARCHAR(100),
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

-- 3. Categorías y Subcategorías
CREATE TABLE categoria (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE subcategoria (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    categoria_id INTEGER NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (categoria_id) REFERENCES categoria(id),
    CONSTRAINT uq_subcategoria_categoria UNIQUE (categoria_id, nombre)
);

-- 4. Proveedores
CREATE TABLE proveedor (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    cuit VARCHAR(20),
    telefono VARCHAR(30),
    email VARCHAR(100),
    direccion VARCHAR(150),
    observaciones TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE
);

-- 5. Productos / Catálogo
CREATE TABLE producto (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo_interno VARCHAR(30) NOT NULL UNIQUE,
    codigo_barras VARCHAR(50) UNIQUE, -- ISBN o EAN opcional
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT,
    autor VARCHAR(100),
    editorial VARCHAR(100),
    categoria_id INTEGER NOT NULL,
    subcategoria_id INTEGER, -- Opcional
    costo_actual NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (costo_actual >= 0),
    precio_venta NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (precio_venta >= 0),
    stock_actual INTEGER NOT NULL DEFAULT 0 CHECK (stock_actual >= 0),
    stock_minimo INTEGER NOT NULL DEFAULT 0 CHECK (stock_minimo >= 0),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (categoria_id) REFERENCES categoria(id),
    FOREIGN KEY (subcategoria_id) REFERENCES subcategoria(id)
);

-- Relación muchos a muchos: Proveedores por Producto
CREATE TABLE producto_proveedor (
    producto_id BIGINT NOT NULL,
    proveedor_id INTEGER NOT NULL,
    PRIMARY KEY (producto_id, proveedor_id),
    FOREIGN KEY (producto_id) REFERENCES producto(id) ON DELETE CASCADE,
    FOREIGN KEY (proveedor_id) REFERENCES proveedor(id) ON DELETE CASCADE
);

-- 6. Compras e Ingresos de Mercadería
CREATE TABLE compra (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    proveedor_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    numero_comprobante VARCHAR(50),
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monto_total NUMERIC(12,2) NOT NULL CHECK (monto_total >= 0),
    observaciones TEXT,
    FOREIGN KEY (proveedor_id) REFERENCES proveedor(id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

CREATE TABLE compra_detalle (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    compra_id BIGINT NOT NULL,
    producto_id BIGINT NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    costo_unitario NUMERIC(12,2) NOT NULL CHECK (costo_unitario >= 0),
    subtotal NUMERIC(12,2) NOT NULL CHECK (subtotal >= 0),
    FOREIGN KEY (compra_id) REFERENCES compra(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES producto(id)
);

-- 7. Ventas y Remitos
CREATE TABLE venta (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monto_total NUMERIC(12,2) NOT NULL CHECK (monto_total >= 0),
    medio_pago medio_pago NOT NULL DEFAULT 'EFECTIVO',
    estado estado_venta NOT NULL DEFAULT 'COMPLETADA',
    observaciones TEXT,
    FOREIGN KEY (cliente_id) REFERENCES cliente(id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

CREATE TABLE venta_detalle (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    venta_id BIGINT NOT NULL,
    producto_id BIGINT NOT NULL,
    cantidad INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(12,2) NOT NULL CHECK (precio_unitario >= 0),
    costo_historico NUMERIC(12,2) NOT NULL CHECK (costo_historico >= 0),
    subtotal NUMERIC(12,2) NOT NULL CHECK (subtotal >= 0),
    FOREIGN KEY (venta_id) REFERENCES venta(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES producto(id)
);

CREATE TABLE remito (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numero_remito VARCHAR(30) NOT NULL UNIQUE,
    venta_id BIGINT NOT NULL UNIQUE,
    fecha_emision TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venta_id) REFERENCES venta(id)
);

-- 8. Movimientos de Stock (Historial / trazabilidad)
CREATE TABLE movimiento_stock (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo tipo_movimiento NOT NULL,
    usuario_id INTEGER NOT NULL,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    observaciones TEXT,
    compra_id BIGINT,
    venta_id BIGINT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id),
    FOREIGN KEY (compra_id) REFERENCES compra(id),
    FOREIGN KEY (venta_id) REFERENCES venta(id)
);

CREATE TABLE movimiento_stock_detalle (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    movimiento_id BIGINT NOT NULL,
    producto_id BIGINT NOT NULL,
    cantidad INTEGER NOT NULL, -- Positivo para entradas, negativo para salidas
    stock_resultante INTEGER NOT NULL,
    FOREIGN KEY (movimiento_id) REFERENCES movimiento_stock(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES producto(id)
);

-- 9. Auditoría del sistema
CREATE TABLE auditoria (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER NOT NULL,
    tabla VARCHAR(70) NOT NULL,
    registro_id BIGINT NOT NULL,
    accion accion_auditoria NOT NULL,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    direccion_ip INET,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id)
);

-- 15. Intentos de login (para limitar fuerza bruta y dejar rastro de seguridad)
-- No tiene clave foránea a propósito: también se registran usuarios que NO existen.
CREATE TABLE intento_login (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    direccion_ip VARCHAR(45) NOT NULL,  -- 45 caracteres alcanzan para IPv6
    exitoso BOOLEAN NOT NULL DEFAULT FALSE,
    fecha TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
);

CREATE INDEX idx_intento_login_usuario_fecha ON intento_login (usuario, fecha);
CREATE INDEX idx_intento_login_ip_fecha ON intento_login (direccion_ip, fecha);

-- ===================== seed.sql ======================
-- Datos iniciales requeridos por el sistema

-- Cliente obligatorio por defecto (idempotente: se puede ejecutar más de una vez)
INSERT INTO cliente (nombre, activo)
SELECT 'CONSUMIDOR FINAL', TRUE
WHERE NOT EXISTS (SELECT 1 FROM cliente WHERE nombre = 'CONSUMIDOR FINAL');
