-- Para una base YA creada: ejecutar una sola vez (los proyectos nuevos la reciben con schema.sql).
CREATE TABLE intento_login (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL,
    direccion_ip VARCHAR(45) NOT NULL,
    exitoso BOOLEAN NOT NULL DEFAULT FALSE,
    fecha TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
);

CREATE INDEX idx_intento_login_usuario_fecha ON intento_login (usuario, fecha);
CREATE INDEX idx_intento_login_ip_fecha ON intento_login (direccion_ip, fecha);
