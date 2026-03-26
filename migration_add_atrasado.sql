-- Migración: Agregar estado "Atrasado" si no existe
-- Ejecutar este script en la base de datos
-- NOTA: Usa nombres de tablas en MINÚSCULAS (tbl_estado, tbl_registro, etc.)

USE desvios_ambientales;

-- Desactivar safe mode temporalmente
SET SQL_SAFE_UPDATES = 0;

-- Verificar si el estado "Atrasado" ya existe
SET @count = (SELECT COUNT(*) FROM tbl_estado WHERE Estado = 'Atrasado');

-- Si no existe, insertarlo
INSERT INTO tbl_estado (Estado, Descripcion, Orden)
SELECT 'Atrasado', 'Registro pendiente con fecha de ejecución vencida', 2
WHERE @count = 0;

-- Actualizar el orden de los demás estados si es necesario
UPDATE tbl_estado SET Orden = 3 WHERE Estado = 'Asignado' AND Orden < 3;
UPDATE tbl_estado SET Orden = 4 WHERE Estado = 'En Proceso' AND Orden < 4;
UPDATE tbl_estado SET Orden = 5 WHERE Estado = 'Enviado' AND Orden < 5;
UPDATE tbl_estado SET Orden = 6 WHERE Estado = 'En Revisión' AND Orden < 6;
UPDATE tbl_estado SET Orden = 7 WHERE Estado = 'Culminado' AND Orden < 7;
UPDATE tbl_estado SET Orden = 8 WHERE Estado = 'Rechazado' AND Orden < 8;
UPDATE tbl_estado SET Orden = 9 WHERE Estado = 'Cerrado' AND Orden < 9;

-- Reactivar safe mode
SET SQL_SAFE_UPDATES = 1;

-- Crear stored procedure para actualizar estados atrasados
DELIMITER $$

DROP PROCEDURE IF EXISTS SP_ActualizarEstadosAtrasados$$
CREATE PROCEDURE SP_ActualizarEstadosAtrasados()
BEGIN
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

-- Verificar los estados
SELECT 'Estados actuales:' as Info;
SELECT idEstado, Estado, Descripcion, Orden FROM tbl_estado ORDER BY Orden;

-- Verificar registros atrasados
SELECT 'Registros atrasados:' as Info;
SELECT r.Codigo, r.FechaEjecucion, e.Estado 
FROM tbl_registro r
JOIN tbl_estado e ON e.idEstado = r.idEstado
WHERE e.Estado = 'Atrasado'
LIMIT 10;

SELECT 'Migración completada exitosamente!' as Resultado;
