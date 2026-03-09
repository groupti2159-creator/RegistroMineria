USE desvios_ambientales;

-- ============================================================
-- SIMPLIFICACIÓN DE ESTADOS A 3 ESTADOS PRINCIPALES
-- ============================================================

-- Actualizar descripciones de los estados principales
UPDATE Tbl_Estado SET Descripcion = 'Registro creado, esperando imágenes' WHERE idEstado = 'EST001';
UPDATE Tbl_Estado SET Descripcion = 'Imágenes subidas, esperando validación' WHERE idEstado = 'EST003';
UPDATE Tbl_Estado SET Descripcion = 'Imágenes validadas y aprobadas' WHERE idEstado = 'EST006';

-- Actualizar registros existentes que usen estados intermedios
UPDATE Tbl_Registro SET idEstado = 'EST001' WHERE idEstado IN ('EST002', 'EST007'); -- Asignado y Rechazado -> Pendiente
UPDATE Tbl_Registro SET idEstado = 'EST003' WHERE idEstado IN ('EST004', 'EST005'); -- Enviado y En Revisión -> En Proceso
UPDATE Tbl_Registro SET idEstado = 'EST006' WHERE idEstado = 'EST008'; -- Cerrado -> Culminado

DELIMITER $$

-- ============================================================
-- ACTUALIZAR SP_CambiarEstado para manejar solo 3 estados
-- ============================================================
DROP PROCEDURE IF EXISTS SP_CambiarEstado$$
CREATE PROCEDURE SP_CambiarEstado(IN p_id CHAR(18), IN p_estado CHAR(18))
BEGIN
    -- Solo permitir cambios a EST001 (Pendiente), EST003 (En Proceso), EST006 (Culminado)
    IF p_estado IN ('EST001', 'EST003', 'EST006') THEN
        UPDATE Tbl_Registro SET idEstado=p_estado WHERE IdRegistro=p_id;
        SELECT ROW_COUNT() AS affected;
    ELSE
        SELECT 0 AS affected, 'Estado no permitido' AS msg;
    END IF;
END$$

-- ============================================================
-- ACTUALIZAR SP_ValidarImagen para cambiar estados correctamente
-- ============================================================
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

    -- Si APROBADA: verificar si todas las imágenes NO rechazadas están aprobadas -> COMPLETADO (EST006)
    IF p_decision = 'APROBADA' THEN
        -- Verificar si hay al menos una imagen aprobada Y no hay imágenes pendientes
        IF EXISTS (
            SELECT 1 FROM Tbl_ImagenRegistro
            WHERE IdRegistro=p_registro AND idTipoImagen='TIM002' AND idEstadoImagen='EIM002'
        ) AND NOT EXISTS (
            SELECT 1 FROM Tbl_ImagenRegistro
            WHERE IdRegistro=p_registro AND idTipoImagen='TIM002' AND idEstadoImagen='EIM001'
        ) THEN
            UPDATE Tbl_Registro SET idEstado='EST006' WHERE IdRegistro=p_registro;
        END IF;
    ELSE
        -- Si RECHAZADA: volver a PENDIENTE (EST001) para que suban nuevas imágenes
        UPDATE Tbl_Registro SET idEstado='EST001' WHERE IdRegistro=p_registro;
    END IF;

    SELECT ROW_COUNT() AS affected;
END$$

-- ============================================================
-- ACTUALIZAR SP_GuardarImagen para cambiar a EN PROCESO
-- ============================================================
DROP PROCEDURE IF EXISTS SP_GuardarImagen$$
CREATE PROCEDURE SP_GuardarImagen(
    IN p_id CHAR(18), IN p_registro CHAR(18),
    IN p_usuario_rol CHAR(18), IN p_tipo CHAR(18),
    IN p_estado CHAR(18), IN p_ruta VARCHAR(300),
    IN p_nombre VARCHAR(100), IN p_tamano INT
)
BEGIN
    DECLARE cnt INT;
    SELECT COUNT(*) INTO cnt FROM Tbl_ImagenRegistro
    WHERE IdRegistro=p_registro AND idTipoImagen=p_tipo AND idEstadoImagen != 'EIM003';
    
    IF cnt < 5 THEN
        INSERT INTO Tbl_ImagenRegistro
            (IdImagen,IdRegistro,IdUsuarioRol,idTipoImagen,idEstadoImagen,RutaImagen,NombreArchivo,TamanoKB)
        VALUES (p_id,p_registro,p_usuario_rol,p_tipo,p_estado,p_ruta,p_nombre,p_tamano);
        
        -- Si es imagen de levantamiento (TIM002), cambiar estado a EN PROCESO (EST003)
        IF p_tipo = 'TIM002' THEN
            UPDATE Tbl_Registro SET idEstado='EST003' WHERE IdRegistro=p_registro;
        END IF;
        
        SELECT 1 AS ok, 'Imagen guardada' AS msg;
    ELSE
        SELECT 0 AS ok, 'Máximo 5 imágenes por tipo' AS msg;
    END IF;
END$$

-- ============================================================
-- ACTUALIZAR SP_CrearRegistro para iniciar en PENDIENTE
-- ============================================================
DROP PROCEDURE IF EXISTS SP_CrearRegistro$$
CREATE PROCEDURE SP_CrearRegistro(
    IN p_id CHAR(18), IN p_codigo VARCHAR(20),
    IN p_fecha DATETIME, IN p_fecha_ejec DATETIME,
    IN p_desc VARCHAR(500), IN p_accion VARCHAR(300),
    IN p_area_rep CHAR(18), IN p_area_res CHAR(18),
    IN p_ubic CHAR(18), IN p_riesgo CHAR(18),
    IN p_tipo CHAR(18), IN p_estado CHAR(18),
    IN p_creador CHAR(18), IN p_personal VARCHAR(100),
    IN p_ccta VARCHAR(100)
)
BEGIN
    -- Siempre crear en estado PENDIENTE (EST001)
    INSERT INTO Tbl_Registro (
        IdRegistro, Codigo, FechaInicio, FechaEjecucion, Descripcion, Accion,
        idAreaReportante, idAreaResponsable, idUbicacion, IdRiesgo,
        IdDescripcionTipo, idEstado, IdUsuarioRolCreador,
        PersonalResponsable, CctaResponsable
    ) VALUES (
        p_id, p_codigo, p_fecha, p_fecha_ejec, p_desc, p_accion,
        p_area_rep, p_area_res, p_ubic, p_riesgo,
        p_tipo, 'EST001', p_creador, p_personal, p_ccta
    );
    SELECT ROW_COUNT() AS affected;
END$$

-- ============================================================
-- ACTUALIZAR SP_ArchivarRegistro para solo archivar COMPLETADOS
-- ============================================================
DROP PROCEDURE IF EXISTS SP_ArchivarRegistro$$
CREATE PROCEDURE SP_ArchivarRegistro(IN p_id CHAR(18), IN p_archivador CHAR(18))
BEGIN
    UPDATE Tbl_Registro
    SET Archivado=1, FechaArchivado=NOW(), IdUsuarioRolArchivador=p_archivador
    WHERE IdRegistro=p_id AND idEstado='EST006';
    SELECT ROW_COUNT() AS affected;
END$$

DELIMITER ;

-- Mostrar resumen de estados
SELECT 'Estados activos:' AS info;
SELECT idEstado, Estado, Descripcion, Orden 
FROM Tbl_Estado 
WHERE idEstado IN ('EST001', 'EST003', 'EST006')
ORDER BY Orden;

SELECT 'Registros por estado:' AS info;
SELECT e.Estado, COUNT(*) as cantidad
FROM Tbl_Registro r
JOIN Tbl_Estado e ON e.idEstado = r.idEstado
WHERE r.Archivado = 0
GROUP BY e.Estado;
