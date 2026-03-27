-- Script para mejorar el stored procedure de actualización de registros
-- Incluye lógica automática para manejar estados Pendiente/Atrasado

USE desvios_ambientales;

DELIMITER $

DROP PROCEDURE IF EXISTS SP_ActualizarRegistro$

CREATE PROCEDURE SP_ActualizarRegistro(
    IN p_idregistro INT,
    IN p_fechainicio DATE,
    IN p_fechaejecucion DATE,
    IN p_descripcion TEXT,
    IN p_accion TEXT,
    IN p_idareareportante INT,
    IN p_idarearesponsable INT,
    IN p_idubicacion INT,
    IN p_idriesgo INT,
    IN p_iddescripciontipo INT,
    IN p_idestado INT,
    IN p_personalresponsable VARCHAR(255),
    IN p_cctaresponsable INT,
    IN p_dniresponsable VARCHAR(20)
)
BEGIN
    DECLARE v_estado_final INT;
    DECLARE v_id_pendiente INT;
    DECLARE v_id_atrasado INT;
    
    -- Obtener IDs de estados Pendiente y Atrasado
    SELECT idEstado INTO v_id_pendiente FROM tbl_estado WHERE Estado = 'Pendiente' LIMIT 1;
    SELECT idEstado INTO v_id_atrasado FROM tbl_estado WHERE Estado = 'Atrasado' LIMIT 1;
    
    -- Determinar el estado final basado en la fecha de ejecución
    SET v_estado_final = p_idestado;
    
    -- Si el estado es Pendiente o Atrasado, validar automáticamente según la fecha
    IF p_idestado IN (v_id_pendiente, v_id_atrasado) THEN
        IF p_fechaejecucion IS NOT NULL THEN
            IF DATE(p_fechaejecucion) < CURDATE() THEN
                -- Fecha vencida -> Atrasado
                SET v_estado_final = v_id_atrasado;
            ELSE
                -- Fecha futura o hoy -> Pendiente
                SET v_estado_final = v_id_pendiente;
            END IF;
        ELSE
            -- Sin fecha de ejecución -> Pendiente por defecto
            SET v_estado_final = v_id_pendiente;
        END IF;
    END IF;
    
    -- Actualizar el registro
    UPDATE tbl_registro
    SET FechaInicio = p_fechainicio,
        FechaEjecucion = p_fechaejecucion,
        Descripcion = p_descripcion,
        Accion = p_accion,
        idAreaReportante = p_idareareportante,
        idAreaResponsable = p_idarearesponsable,
        idUbicacion = p_idubicacion,
        idRiesgo = p_idriesgo,
        IdDescripcionTipo = p_iddescripciontipo,
        idEstado = v_estado_final,
        PersonalResponsable = p_personalresponsable,
        CctaResponsable = NULLIF(p_cctaresponsable, 0),
        DniResponsable = p_dniresponsable
    WHERE IdRegistro = p_idregistro;
    
    -- Retornar el estado final aplicado
    SELECT v_estado_final AS estado_aplicado, 
           (SELECT Estado FROM tbl_estado WHERE idEstado = v_estado_final) AS nombre_estado;
END$

DELIMITER ;

SELECT '✅ Stored procedure SP_ActualizarRegistro mejorado!' as Resultado;
SELECT 'Ahora maneja automáticamente la lógica Pendiente/Atrasado' as Info;
