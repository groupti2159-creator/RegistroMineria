-- Agregar campo personalreportante a tbl_registro
USE desvios_ambientales;

ALTER TABLE tbl_registro 
ADD COLUMN personalreportante INT NULL AFTER idareareportante,
ADD CONSTRAINT fk_personal_reportante 
    FOREIGN KEY (personalreportante) 
    REFERENCES tbl_persona(id) 
    ON DELETE SET NULL;

-- Verificar
DESCRIBE tbl_registro;
