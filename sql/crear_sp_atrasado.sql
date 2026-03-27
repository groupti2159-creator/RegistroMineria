-- Script SIMPLIFICADO: Solo crear los stored procedures necesarios
-- No modificamos el orden de estados (puede quedar en 9)

USE desvios_ambientales;

-- Desactivar safe mode temporalmente
SET SQL_SAFE_UPDATES = 0;

-- Crear stored procedure para actualizar estados atrasados
DELIMITER $$

DROP PROCEDURE IF EXISTS SP_ActualizarEstadosAtrasados$$
CREATE PROCEDURE SP_ActualizarEstadosAtrasados()
BEGIN
    -- TODOS los DECLARE deben ir al principio
    DECLARE old_sql_safe_updates INT;
    DECLARE v_id_atrasado INT;
    
    -- Ahora las asignaciones
    SET old_sql_safe_updates = @@SQL_SAFE_UPDATES;
    SET SQL_SAFE_UPDATES = 0;
    
    -- Obtener el ID del estado "Atrasado"
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

-- Reactivar safe mode
SET SQL_SAFE_UPDATES = 1;

-- Verificar que los stored procedures se crearon
SELECT '=== Stored Procedures creados ===' as Info;
SHOW PROCEDURE STATUS WHERE Db = 'desvios_ambientales' AND Name IN ('SP_ActualizarEstadosAtrasados', 'SP_DashboardStats');

SELECT '✅ Stored procedures creados exitosamente!' as Resultado;
SELECT 'Ahora puedes reiniciar tu aplicación Flask' as Siguiente_Paso;
