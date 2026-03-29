-- Script para actualizar los stored procedures de estadísticas
-- Incluye el estado "Atrasado" en las columnas de pendientes y atrasados

USE desvios_ambientales;

DELIMITER $$

-- SP: Estadísticas por área (con columna separada para Atrasado)
DROP PROCEDURE IF EXISTS SP_EstadisticasAreas$$
CREATE PROCEDURE SP_EstadisticasAreas(IN p_fecha_ini DATE, IN p_fecha_fin DATE)
BEGIN
    SELECT ar.AreaReportante AS area_responsable,
        COUNT(*) AS total,
        SUM(CASE WHEN e.Estado='Culminado' THEN 1 ELSE 0 END) AS culminado,
        SUM(CASE WHEN e.Estado='Pendiente' THEN 1 ELSE 0 END) AS pendiente,
        SUM(CASE WHEN e.Estado='Atrasado' THEN 1 ELSE 0 END) AS atrasado,
        SUM(CASE WHEN e.Estado IN ('En Proceso','Enviado','En Revisión') THEN 1 ELSE 0 END) AS proceso
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado=r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante=r.idAreaReportante
    WHERE r.Archivado=0
      AND (p_fecha_ini IS NULL OR DATE(r.FechaCreacion) >= p_fecha_ini)
      AND (p_fecha_fin IS NULL OR DATE(r.FechaCreacion) <= p_fecha_fin)
    GROUP BY ar.idAreaReportante, ar.AreaReportante
    ORDER BY total DESC;
END$$

-- SP: Estadísticas por cuenta responsable (con columna separada para Atrasado)
DROP PROCEDURE IF EXISTS SP_EstadisticasCcta$$
CREATE PROCEDURE SP_EstadisticasCcta(IN p_fecha_ini DATE, IN p_fecha_fin DATE)
BEGIN
    SELECT 
        IFNULL(ccta.AreaReportante, 'Sin asignar') AS ccta_responsable,
        COUNT(*) AS total,
        SUM(CASE WHEN e.Estado='Culminado' THEN 1 ELSE 0 END) AS culminado,
        SUM(CASE WHEN e.Estado='Pendiente' THEN 1 ELSE 0 END) AS pendiente,
        SUM(CASE WHEN e.Estado='Atrasado' THEN 1 ELSE 0 END) AS atrasado,
        SUM(CASE WHEN e.Estado IN ('En Proceso','Enviado','En Revisión') THEN 1 ELSE 0 END) AS proceso
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado=r.idEstado
    LEFT JOIN tbl_areareportante ccta ON ccta.idAreaReportante = r.CctaResponsable
    WHERE r.Archivado=0
      AND (p_fecha_ini IS NULL OR DATE(r.FechaCreacion) >= p_fecha_ini)
      AND (p_fecha_fin IS NULL OR DATE(r.FechaCreacion) <= p_fecha_fin)
    GROUP BY ccta.idAreaReportante, ccta.AreaReportante
    ORDER BY total DESC;
END$$

-- SP: Estadísticas por tipo (solo pendientes y atrasados)
DROP PROCEDURE IF EXISTS SP_Estadisticas_Tipos_Pendientes$$
CREATE PROCEDURE SP_Estadisticas_Tipos_Pendientes(IN p_fecha_ini DATE, IN p_fecha_fin DATE)
BEGIN
    SELECT dt.DescripcionTipo AS tipo_descripcion,
        SUM(CASE WHEN e.Estado = 'Pendiente' THEN 1 ELSE 0 END) AS pendiente,
        SUM(CASE WHEN e.Estado = 'Atrasado' THEN 1 ELSE 0 END) AS atrasado,
        SUM(CASE WHEN e.Estado IN ('Pendiente','Atrasado') THEN 1 ELSE 0 END) AS cantidad_pendiente
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado=r.idEstado
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo=r.IdDescripcionTipo
    WHERE r.Archivado=0
      AND e.Estado IN ('Pendiente','Atrasado')
      AND (p_fecha_ini IS NULL OR DATE(r.FechaCreacion) >= p_fecha_ini)
      AND (p_fecha_fin IS NULL OR DATE(r.FechaCreacion) <= p_fecha_fin)
    GROUP BY dt.IdDescripcionTipo, dt.DescripcionTipo
    HAVING cantidad_pendiente > 0
    ORDER BY cantidad_pendiente DESC;
END$$

DELIMITER ;

SELECT '✅ Stored procedures de estadísticas actualizados!' as Resultado;
SELECT 'Ahora las estadísticas incluyen el estado Atrasado' as Info;
