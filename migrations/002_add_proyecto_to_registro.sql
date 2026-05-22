-- Migración: Agregar columna IdProyecto a tbl_registro
-- Fecha: 2026-05-21
-- Descripción: Agregar soporte para filtrado de reportes por proyecto

USE desvios_ambientales;

-- Agregar columna IdProyecto a tbl_registro
ALTER TABLE tbl_registro 
ADD COLUMN IdProyecto INT NOT NULL DEFAULT 1 AFTER IdRegistro,
ADD FOREIGN KEY (IdProyecto) REFERENCES tbl_proyecto(idproyecto);

-- Actualizar SP_ListarRegistros para incluir filtro por proyecto
DELIMITER $$

DROP PROCEDURE IF EXISTS SP_ListarRegistros$$
CREATE PROCEDURE SP_ListarRegistros(IN p_estado VARCHAR(50), IN p_proyecto_id INT)
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion, r.PersonalResponsable, r.DniResponsable,
           r.CctaResponsable,
           ccta.AreaReportante AS NombreCctaResponsable,
           e.Estado, e.idEstado,
           ar.AreaReportante, ars.AreaResponsable,
           ub.Ubicacion, ri.Riesgo, dt.DescripcionTipo,
           u.NombreCompleto AS Creador,
           (SELECT COUNT(*) FROM tbl_imagenregistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen=1 AND img.idEstadoImagen != 3) AS cnt_evidencias,
           (SELECT COUNT(*) FROM tbl_imagenregistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen=2 AND img.idEstadoImagen != 3) AS cnt_levantamientos
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_arearesponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN tbl_ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    JOIN tbl_usuariorol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    LEFT JOIN tbl_areareportante ccta ON ccta.idAreaReportante = r.CctaResponsable
    WHERE r.Archivado = 0
      AND r.IdProyecto = p_proyecto_id
      AND (p_estado IS NULL OR p_estado = '' OR e.Estado = p_estado)
    ORDER BY r.FechaCreacion DESC;
END$$

-- Actualizar SP_ListarRegistrosSupervisor para incluir filtro por proyecto
DROP PROCEDURE IF EXISTS SP_ListarRegistrosSupervisor$$
CREATE PROCEDURE SP_ListarRegistrosSupervisor(IN p_estado VARCHAR(50), IN p_proyecto_id INT)
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion, r.PersonalResponsable, r.DniResponsable,
           r.CctaResponsable,
           ccta.AreaReportante AS NombreCctaResponsable,
           e.Estado, e.idEstado,
           ar.AreaReportante, ars.AreaResponsable,
           ub.Ubicacion, ri.Riesgo, dt.DescripcionTipo,
           u.NombreCompleto AS Creador,
           (SELECT COUNT(*) FROM tbl_imagenregistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen=1 AND img.idEstadoImagen != 3) AS cnt_evidencias,
           (SELECT COUNT(*) FROM tbl_imagenregistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen=2 AND img.idEstadoImagen != 3) AS cnt_levantamientos
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_arearesponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN tbl_ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    JOIN tbl_usuariorol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    LEFT JOIN tbl_areareportante ccta ON ccta.idAreaReportante = r.CctaResponsable
    WHERE r.Archivado = 0
      AND r.IdProyecto = p_proyecto_id
      AND (p_estado IS NULL OR p_estado = '' OR e.Estado = p_estado)
    ORDER BY r.FechaCreacion DESC;
END$$

-- Actualizar SP_CrearRegistro para incluir IdProyecto
DROP PROCEDURE IF EXISTS SP_CrearRegistro$$
CREATE PROCEDURE SP_CrearRegistro(
    IN p_codigo VARCHAR(20),
    IN p_fecha DATETIME, IN p_fecha_ejec DATETIME,
    IN p_desc VARCHAR(500), IN p_accion VARCHAR(300),
    IN p_area_rep INT, IN p_personal_rep INT,
    IN p_area_res INT, IN p_ubic VARCHAR(100),
    IN p_riesgo INT, IN p_tipo INT,
    IN p_riesgo_critico INT, IN p_estado INT,
    IN p_creador INT, IN p_personal_res INT,
    IN p_ccta INT, IN p_dni VARCHAR(20),
    IN p_origen INT, IN p_proyecto INT
)
BEGIN
    INSERT INTO tbl_registro (
        Codigo, FechaInicio, FechaEjecucion, Descripcion, Accion,
        idAreaReportante, idAreaResponsable, idUbicacion, IdRiesgo,
        IdDescripcionTipo, idEstado, IdUsuarioRolCreador,
        PersonalResponsable, DniResponsable, CctaResponsable, IdProyecto
    ) VALUES (
        p_codigo, p_fecha, p_fecha_ejec, p_desc, p_accion,
        p_area_rep, p_area_res, p_ubic, p_riesgo,
        p_tipo, p_estado, p_creador, p_personal_res,
        NULLIF(p_dni, ''), NULLIF(p_ccta, 0), p_proyecto
    );
    SELECT LAST_INSERT_ID() AS idregistro;
END$$

DELIMITER ;
