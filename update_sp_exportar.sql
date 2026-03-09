-- Actualizar SP_ExportarRegistros para incluir IdRegistro
-- Esto permite consultar las imágenes de cada registro en la exportación

DELIMITER $$

DROP PROCEDURE IF EXISTS SP_ExportarRegistros$$
CREATE PROCEDURE SP_ExportarRegistros()
BEGIN
    SELECT r.IdRegistro, r.Codigo, DATE(r.FechaInicio) AS Fecha,
           DATE(r.FechaEjecucion) AS FechaEjecucion,
           ar.AreaReportante, ub.Ubicacion,
           r.Descripcion, dt.DescripcionTipo,
           ri.Riesgo, e.Estado, r.Accion,
           ars.AreaResponsable, r.PersonalResponsable,
           r.FechaCreacion
    FROM Tbl_Registro r
    JOIN Tbl_Estado e ON e.idEstado=r.idEstado
    JOIN Tbl_AreaReportante ar ON ar.idAreaReportante=r.idAreaReportante
    JOIN Tbl_AreaResponsable ars ON ars.idAreaResponsable=r.idAreaResponsable
    JOIN Tbl_Ubicacion ub ON ub.idUbicacion=r.idUbicacion
    JOIN Tbl_Riesgo ri ON ri.IdRiesgo=r.IdRiesgo
    JOIN Tbl_DescripcionTipo dt ON dt.IdDescripcionTipo=r.IdDescripcionTipo
    WHERE r.Archivado=0
    ORDER BY r.FechaCreacion DESC;
END$$

DELIMITER ;
