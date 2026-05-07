-- Cambiar campo idubicacion a texto libre
USE desvios_ambientales;

-- Eliminar foreign key
ALTER TABLE tbl_registro DROP FOREIGN KEY tbl_registro_ibfk_3;

-- Cambiar tipo de dato
ALTER TABLE tbl_registro 
MODIFY COLUMN idubicacion VARCHAR(200) NOT NULL;

-- Renombrar columna
ALTER TABLE tbl_registro 
CHANGE COLUMN idubicacion ubicacion VARCHAR(200) NOT NULL;

-- Verificar
DESCRIBE tbl_registro;
