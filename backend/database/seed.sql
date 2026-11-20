-- Datos iniciales requeridos por el sistema

-- Cliente obligatorio por defecto (idempotente: se puede ejecutar más de una vez)
INSERT INTO cliente (nombre, activo)
SELECT 'CONSUMIDOR FINAL', TRUE
WHERE NOT EXISTS (SELECT 1 FROM cliente WHERE nombre = 'CONSUMIDOR FINAL');
