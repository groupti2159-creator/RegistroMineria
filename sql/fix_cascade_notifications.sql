-- Script para activar el borrado en cascada en la tabla de notificaciones
-- Esto permite que al borrar un usuario, sus roles y notificaciones se borren automáticamente sin errores de FK.

USE desvios_ambientales;

-- 1. Identificar y eliminar la restricción actual si existe
-- El nombre por defecto suele ser Tbl_Notificacion_ibfk_1
SET @constraint_name = (
    SELECT CONSTRAINT_NAME 
    FROM information_schema.KEY_COLUMN_USAGE 
    WHERE TABLE_NAME = 'Tbl_Notificacion' 
    AND COLUMN_NAME = 'IdUsuarioRol' 
    AND TABLE_SCHEMA = DATABASE()
    LIMIT 1
);

SET @query = CONCAT('ALTER TABLE Tbl_Notificacion DROP FOREIGN KEY ', @constraint_name);
PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. Crear la nueva restricción con ON DELETE CASCADE
ALTER TABLE Tbl_Notificacion 
ADD CONSTRAINT fk_notificacion_usuariorol_cascade 
FOREIGN KEY (IdUsuarioRol) REFERENCES Tbl_UsuarioRol(IdUsuarioRol) 
ON DELETE CASCADE;

SELECT 'Cascada activada correctamente en Tbl_Notificacion' AS Resultado;
