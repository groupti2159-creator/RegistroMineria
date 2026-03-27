-- Verificar si existe el stored procedure y ver su definición

-- 1. Ver si existe el SP
SELECT 
    ROUTINE_NAME,
    ROUTINE_TYPE,
    CREATED,
    LAST_ALTERED
FROM information_schema.ROUTINES
WHERE ROUTINE_SCHEMA = DATABASE()
AND ROUTINE_NAME = 'sp_obtenermodulospersonalizados';

-- 2. Ver la definición del SP
SHOW CREATE PROCEDURE sp_obtenermodulospersonalizados;

-- 3. Ver todas las tablas que empiezan con tbl_
SHOW TABLES LIKE 'tbl_%';
