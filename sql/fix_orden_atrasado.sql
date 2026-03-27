-- Script para corregir el orden del estado "Atrasado" y crear stored procedures
-- El estado ya existe pero está en orden 9, necesitamos moverlo a orden 2

USE desvios_ambientales;

-- Desactivar safe mode temporalmente
SET SQL_SAFE_UPDATES = 0;

-- Actualizar el orden de "Atrasado" a 2
UPDATE tbl_estado SET Orden = 2 WHERE Estado = 'Atrasado';

-- Ajustar el orden de los demás estados
UPDATE tbl_estado SET Orden = 3 WHERE Estado = 'Asignado';
UPDATE tbl_estado SET Orden = 4 WHERE Estado = 'En Proceso';
UPDATE tbl_estado SET Orden = 5 WHERE Estado = 'Enviado';
UPDATE tbl_estado SET Orden = 6 WHERE Estado = 'En Revisión';
UPDATE tbl_estado SET Orden = 7 WHERE Estado = 'Culminado';
UPDATE tbl_estado SET Orden = 8 WHERE Estado = 'Rechazado';
UPDATE tbl_estado SET Orden = 9 WHERE Estado = 'Cerrado';

-- Crear stored procedure para actualizar estados atrasados
DELIMITER $$

DROP PROCEDURE IF EXISTS SP_ActualizarEstadosAtrasados$$
CREATE PROCEDURE SP_ActualizarEstadosAtrasados()
BEGIN
    -- Desactivar safe mode dentro del procedimiento
    DECLARE old_sql_safe_updates INT;
    SET old_sql_safe_updates = @@SQL_SAFE_UPDATES;
    SET SQL_SAFE_UPDATES = 0;
    
    -- Obtener el ID del estado "Atrasado"
    DECLARE v_id_atrasado INT;
    SELECT idEstado INTO v_id_atrasado FROM tbl_estado WHERE Estado = 'Atrasado' LIMIT 1;
    
    -- Actualizar registros Pendientes con fecha de ejecución vencida a Atrasado
    UPDATE tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    SET r.idEstado = v_id_atrasado
    WHERE e.Estado = 'Pendiente'
      AND r.FechaEjecucion IS NOT NULL
      AND DATE(r.FechaEjecucion) < CURDATE()
      AND r.Archivado = 0;
    
    -- Restaurar safe mode
    SET SQL_SAFE_UPDATES = old_sql_safe_updates;
    
    SELECT ROW_COUNT() AS registros_actualizados;
END$$

DELIMITER ;

-- Actualizar el SP_DashboardStats para incluir Atrasado en pendientes
DELIMITER $$

DROP PROCEDURE IF EXISTS SP_DashboardStats$$
CREATE PROCEDURE SP_DashboardStats()
BEGIN
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN e.Estado = 'Culminado' THEN 1 ELSE 0 END) AS culminados,
        SUM(CASE WHEN e.Estado IN ('En Proceso','Enviado','En Revisión') THEN 1 ELSE 0 END) AS en_proceso,
        SUM(CASE WHEN e.Estado IN ('Pendiente','Atrasado') THEN 1 ELSE 0 END) AS pendientes
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    WHERE r.Archivado = 0;
END$$

DELIMITER ;

-- Ejecutar el procedimiento para actualizar registros existentes
CALL SP_ActualizarEstadosAtrasados();

-- Reactivar safe mode
SET SQL_SAFE_UPDATES = 1;

-- Verificar los estados con el nuevo orden
SELECT '=== Estados actuales (orden corregido) ===' as Info;
SELECT idEstado, Estado, Descripcion, Orden FROM tbl_estado ORDER BY Orden;

-- Verificar que el stored procedure existe
SELECT '=== Stored Procedures creados ===' as Info;
SHOW PROCEDURE STATUS WHERE Db = 'desvios_ambientales' AND Name IN ('SP_ActualizarEstadosAtrasados', 'SP_DashboardStats');

-- Verificar registros atrasados
SELECT '=== Registros marcados como Atrasado ===' as Info;
SELECT COUNT(*) as total_atrasados FROM tbl_registro r
JOIN tbl_estado e ON e.idEstado = r.idEstado
WHERE e.Estado = 'Atrasado';

SELECT '✅ Migración completada exitosamente!' as Resultado;
