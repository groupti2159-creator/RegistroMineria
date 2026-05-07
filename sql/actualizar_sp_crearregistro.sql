-- Actualizar SP_CrearRegistro para incluir personalreportante y riesgo_critico_id
USE desvios_ambientales;

DELIMITER $$

DROP PROCEDURE IF EXISTS SP_CrearRegistro$$
CREATE PROCEDURE SP_CrearRegistro(
    IN p_codigo VARCHAR(20),
    IN p_fecha DATETIME, IN p_fecha_ejec DATETIME,
    IN p_desc VARCHAR(500), IN p_accion VARCHAR(300),
    IN p_area_rep INT, IN p_personal_rep INT, IN p_area_res INT,
    IN p_ubic VARCHAR(200), IN p_riesgo INT,
    IN p_tipo INT, IN p_riesgo_critico INT, IN p_estado INT,
    IN p_creador INT, IN p_personal_resp_id INT,
    IN p_ccta INT, IN p_dni VARCHAR(20)
)
BEGIN
    INSERT INTO tbl_registro (
        Codigo, FechaInicio, FechaEjecucion, Descripcion, Accion,
        idAreaReportante, personalreportante, idAreaResponsable, ubicacion, IdRiesgo,
        IdDescripcionTipo, riesgo_critico_id, idEstado, IdUsuarioRolCreador,
        personalresponsable_id, DniResponsable, CctaResponsable
    ) VALUES (
        p_codigo, p_fecha, p_fecha_ejec, p_desc, p_accion,
        p_area_rep, NULLIF(p_personal_rep, 0), p_area_res, p_ubic, p_riesgo,
        p_tipo, NULLIF(p_riesgo_critico, 0), p_estado, p_creador, NULLIF(p_personal_resp_id, 0),
        NULLIF(p_dni, ''), NULLIF(p_ccta, 0)
    );
    SELECT LAST_INSERT_ID() AS idregistro;
END$$

DELIMITER ;

