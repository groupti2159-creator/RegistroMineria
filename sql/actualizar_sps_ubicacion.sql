-- Actualizar todos los SPs para usar ubicacion como texto en lugar de JOIN
USE desvios_ambientales;

DELIMITER $$

-- SP_ListarRegistros
DROP PROCEDURE IF EXISTS SP_ListarRegistros$$
CREATE PROCEDURE SP_ListarRegistros(IN p_estado VARCHAR(50))
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion,
           ar.AreaReportante, ar.idAreaReportante,
           ars.AreaResponsable, ars.idAreaResponsable,
           r.ubicacion AS Ubicacion,
           ri.Riesgo, ri.IdRiesgo,
           dt.DescripcionTipo, dt.IdDescripcionTipo,
           e.Estado, e.idEstado,
           r.PersonalResponsable, r.DniResponsable,
           r.FechaCreacion, r.FechaActualizacion
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_arearesponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    WHERE (p_estado IS NULL OR e.Estado = p_estado)
      AND (r.Archivado IS NULL OR r.Archivado = 0)
    ORDER BY r.FechaCreacion DESC;
END$$

-- SP_ListarRegistrosSupervisor
DROP PROCEDURE IF EXISTS SP_ListarRegistrosSupervisor$$
CREATE PROCEDURE SP_ListarRegistrosSupervisor(IN p_estado VARCHAR(50))
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion,
           ar.AreaReportante, ar.idAreaReportante,
           ars.AreaResponsable, ars.idAreaResponsable,
           r.ubicacion AS Ubicacion,
           ri.Riesgo, ri.IdRiesgo,
           dt.DescripcionTipo, dt.IdDescripcionTipo,
           e.Estado, e.idEstado,
           r.PersonalResponsable, r.DniResponsable,
           r.FechaCreacion, r.FechaActualizacion
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_arearesponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    WHERE (p_estado IS NULL OR e.Estado = p_estado)
      AND (r.Archivado IS NULL OR r.Archivado = 0)
    ORDER BY r.FechaCreacion DESC;
END$$

-- SP_DetalleRegistro
DROP PROCEDURE IF EXISTS SP_DetalleRegistro$$
CREATE PROCEDURE SP_DetalleRegistro(IN p_id INT)
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion, r.NotasLevantamiento,
           ar.AreaReportante, ar.idAreaReportante,
           ars.AreaResponsable, ars.idAreaResponsable,
           r.ubicacion AS Ubicacion, NULL AS idUbicacion,
           ri.Riesgo, ri.IdRiesgo,
           dt.DescripcionTipo, dt.IdDescripcionTipo,
           e.Estado, e.idEstado,
           r.PersonalResponsable, r.DniResponsable,
           r.FechaCreacion, r.FechaActualizacion
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_arearesponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    WHERE r.IdRegistro = p_id;
END$$

-- SP_HistorialAdmin
DROP PROCEDURE IF EXISTS SP_HistorialAdmin$$
CREATE PROCEDURE SP_HistorialAdmin()
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, ar.AreaReportante,
           r.ubicacion AS Ubicacion,
           ri.Riesgo, e.Estado
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_usuariorol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    WHERE (r.Archivado IS NULL OR r.Archivado = 0)
    ORDER BY r.FechaCreacion DESC;
END$$

-- SP_HistorialSupervisor
DROP PROCEDURE IF EXISTS SP_HistorialSupervisor$$
CREATE PROCEDURE SP_HistorialSupervisor(IN p_usuario_rol INT)
BEGIN
    SELECT DISTINCT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, ar.AreaReportante,
           r.ubicacion AS Ubicacion,
           ri.Riesgo, e.Estado
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_usuariorol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    WHERE (r.Archivado IS NULL OR r.Archivado = 0)
    ORDER BY r.FechaCreacion DESC;
END$$

-- SP_ExportarExcel
DROP PROCEDURE IF EXISTS SP_ExportarExcel$$
CREATE PROCEDURE SP_ExportarExcel()
BEGIN
    SELECT r.Codigo, r.FechaInicio, r.FechaEjecucion,
           ar.AreaReportante, ars.AreaResponsable,
           r.ubicacion AS Ubicacion,
           ri.Riesgo, dt.DescripcionTipo,
           r.Descripcion, r.Accion,
           e.Estado, r.PersonalResponsable
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado=r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante=r.idAreaReportante
    JOIN tbl_arearesponsable ars ON ars.idAreaResponsable=r.idAreaResponsable
    JOIN tbl_riesgo ri ON ri.IdRiesgo=r.IdRiesgo
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo=r.IdDescripcionTipo
    WHERE (r.Archivado IS NULL OR r.Archivado=0)
    ORDER BY r.FechaCreacion DESC;
END$$

-- SP_ActualizarRegistro
DROP PROCEDURE IF EXISTS SP_ActualizarRegistro$$
CREATE PROCEDURE SP_ActualizarRegistro(
    IN p_id INT, IN p_fecha DATETIME, IN p_fecha_ejec DATETIME,
    IN p_desc VARCHAR(500), IN p_accion VARCHAR(300),
    IN p_area_rep INT, IN p_area_res INT,
    IN p_ubic VARCHAR(200), IN p_riesgo INT,
    IN p_tipo INT, IN p_estado INT,
    IN p_personal VARCHAR(100), IN p_ccta INT,
    IN p_dni VARCHAR(20)
)
BEGIN
    UPDATE tbl_registro SET
        FechaInicio=p_fecha, FechaEjecucion=p_fecha_ejec,
        Descripcion=p_desc, Accion=p_accion,
        idAreaReportante=p_area_rep, idAreaResponsable=p_area_res,
        ubicacion=p_ubic, IdRiesgo=p_riesgo,
        IdDescripcionTipo=p_tipo, idEstado=p_estado,
        PersonalResponsable=p_personal,
        DniResponsable=NULLIF(p_dni, ''),
        CctaResponsable=NULLIF(p_ccta, 0)
    WHERE IdRegistro=p_id;
END$$

DELIMITER ;
