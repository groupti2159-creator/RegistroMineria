-- Actualizar tabla tbl_descripciontipo para tener solo SEGURIDAD y MEDIO AMBIENTE
USE desvios_ambientales;

-- Limpiar tabla
TRUNCATE TABLE tbl_descripciontipo;

-- Insertar solo dos tipos
INSERT INTO tbl_descripciontipo (iddescripciontipo, descripciontipo) VALUES
(1, 'SEGURIDAD'),
(2, 'MEDIO AMBIENTE');

-- Verificar
SELECT * FROM tbl_descripciontipo ORDER BY iddescripciontipo;
