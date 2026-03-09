USE desvios_ambientales;

DELIMITER $$

-- Crear un nuevo SP para eliminar imágenes físicamente
DROP PROCEDURE IF EXISTS SP_EliminarImagen$$
CREATE PROCEDURE SP_EliminarImagen(
    IN p_imagen CHAR(18)
)
BEGIN
    -- Eliminar físicamente la imagen de la base de datos
    DELETE FROM Tbl_ImagenRegistro WHERE IdImagen=p_imagen;
    SELECT ROW_COUNT() AS affected;
END$$

-- Actualizar SP_ValidarImagen
DROP PROCEDURE IF EXISTS SP_ValidarImagen$$
CREATE PROCEDURE SP_ValidarImagen(
    IN p_id_historial CHAR(18), 
    IN p_imagen CHAR(18), 
    IN p_registro CHAR(18),
    IN p_revisor CHAR(18), 
    IN p_decision VARCHAR(20),
    IN p_comentario VARCHAR(300)
)
BEGIN
    DECLARE v_estado CHAR(18);
    IF p_decision = 'APROBADA' THEN SET v_estado = 'EIM002';
    ELSE SET v_estado = 'EIM003'; END IF;

    UPDATE Tbl_ImagenRegistro
    SET idEstadoImagen=v_estado, IdUsuarioRolRevisor=p_revisor,
        FechaRevision=NOW(), MotivoRechazo=IF(p_decision='RECHAZADA',p_comentario,NULL)
    WHERE IdImagen=p_imagen;

    INSERT INTO Tbl_HistorialAprobacion
        (IdHistorial,IdImagen,IdRegistro,IdUsuarioRolRevisor,DecisionTomada,Comentarios)
    VALUES (p_id_historial,p_imagen,p_registro,p_revisor,p_decision,p_comentario);

    -- Si APROBADA: cambiar a COMPLETADO
    IF p_decision = 'APROBADA' THEN
        UPDATE Tbl_Registro SET idEstado='EST006' WHERE IdRegistro=p_registro;
    ELSE
        -- Si RECHAZADA: volver a PENDIENTE
        UPDATE Tbl_Registro SET idEstado='EST001' WHERE IdRegistro=p_registro;
    END IF;

    SELECT ROW_COUNT() AS affected;
END$$

DELIMITER ;

SELECT '✅ Stored procedures actualizados correctamente' AS resultado;
SELECT 'Las imágenes eliminadas con X se borrarán físicamente de la base de datos' AS nota;
