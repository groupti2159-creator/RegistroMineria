-- Script para corregir referencias de tablas en stored procedures
-- Convierte Tbl_* a tbl_* para compatibilidad con Railway (Linux)
-- Generado automáticamente

USE desvios_ambientales;

-- Corregir sp_actualizarregistro
DROP PROCEDURE IF EXISTS sp_actualizarregistro;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_actualizarregistro`(
    IN p_id CHAR(18), IN p_fecha DATETIME, IN p_fecha_ejec DATETIME,
    IN p_desc VARCHAR(500), IN p_accion VARCHAR(300),
    IN p_area_rep CHAR(18), IN p_area_res CHAR(18),
    IN p_ubic CHAR(18), IN p_riesgo CHAR(18),
    IN p_tipo CHAR(18), IN p_estado CHAR(18),
    IN p_personal VARCHAR(100), IN p_ccta VARCHAR(100)
)
BEGIN
    UPDATE tbl_registro SET
        FechaInicio=p_fecha, FechaEjecucion=p_fecha_ejec,
        Descripcion=p_desc, Accion=p_accion,
        idAreaReportante=p_area_rep, idAreaResponsable=p_area_res,
        idUbicacion=p_ubic, IdRiesgo=p_riesgo,
        IdDescripcionTipo=p_tipo, idEstado=p_estado,
        PersonalResponsable=p_personal, CctaResponsable=p_ccta
    WHERE IdRegistro=p_id;
    SELECT ROW_COUNT() AS affected;
END$$

DELIMITER ;

-- Corregir sp_archivarregistro
DROP PROCEDURE IF EXISTS sp_archivarregistro;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_archivarregistro`(IN p_id CHAR(18), IN p_archivador CHAR(18))
BEGIN
    UPDATE tbl_registro
    SET Archivado=1, FechaArchivado=NOW(), IdUsuarioRolArchivador=p_archivador
    WHERE IdRegistro=p_id AND idEstado='EST006';
    SELECT ROW_COUNT() AS affected;
END$$

DELIMITER ;

-- Corregir sp_cambiarestado
DROP PROCEDURE IF EXISTS sp_cambiarestado;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_cambiarestado`(IN p_id CHAR(18), IN p_estado CHAR(18))
BEGIN
    -- Solo permitir cambios a EST001 (Pendiente), EST003 (En Proceso), EST006 (Culminado)
    IF p_estado IN ('EST001', 'EST003', 'EST006') THEN
        UPDATE tbl_registro SET idEstado=p_estado WHERE IdRegistro=p_id;
        SELECT ROW_COUNT() AS affected;
    ELSE
        SELECT 0 AS affected, 'Estado no permitido' AS msg;
    END IF;
END$$

DELIMITER ;

-- Corregir sp_contarnotificaciones
DROP PROCEDURE IF EXISTS sp_contarnotificaciones;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_contarnotificaciones`(IN p_usuario_rol CHAR(18))
BEGIN
    SELECT COUNT(*) AS total FROM tbl_notificacion
    WHERE IdUsuarioRol=p_usuario_rol AND Leida=0;
END$$

DELIMITER ;

-- Corregir sp_crearnotificacion
DROP PROCEDURE IF EXISTS sp_crearnotificacion;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_crearnotificacion`(
    IN p_id CHAR(18), IN p_usuario_rol CHAR(18),
    IN p_mensaje VARCHAR(300), IN p_tipo VARCHAR(20),
    IN p_registro CHAR(18)
)
BEGIN
    INSERT INTO tbl_notificacion(IdNotificacion,IdUsuarioRol,Mensaje,Tipo,IdRegistro)
    VALUES(p_id,p_usuario_rol,p_mensaje,p_tipo,p_registro);
END$$

DELIMITER ;

-- Corregir sp_crearregistro
DROP PROCEDURE IF EXISTS sp_crearregistro;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_crearregistro`(
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
    INSERT INTO tbl_registro (
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

DELIMITER ;

-- Corregir sp_dashboardstats
DROP PROCEDURE IF EXISTS sp_dashboardstats;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_dashboardstats`()
BEGIN
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN e.Estado = 'Culminado' THEN 1 ELSE 0 END) AS culminados,
        SUM(CASE WHEN e.Estado IN ('En Proceso','Enviado','En Revisión') THEN 1 ELSE 0 END) AS en_proceso,
        SUM(CASE WHEN e.Estado = 'Pendiente' THEN 1 ELSE 0 END) AS pendientes
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    WHERE r.Archivado = 0;
END$$

DELIMITER ;

-- Corregir sp_detalleregistro
DROP PROCEDURE IF EXISTS sp_detalleregistro;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_detalleregistro`(IN p_id CHAR(18))
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion, r.NotasLevantamiento, r.PersonalResponsable, r.CctaResponsable,
           e.Estado, e.idEstado,
           ar.AreaReportante, ar.idAreaReportante,
           ars.AreaResponsable, ars.idAreaResponsable,
           ub.Ubicacion, ub.idUbicacion,
           ri.Riesgo, ri.IdRiesgo,
           dt.DescripcionTipo, dt.IdDescripcionTipo,
           u.NombreCompleto AS Creador,
           r.FechaCreacion, r.Archivado
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_arearesponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN tbl_ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    JOIN tbl_usuarioRol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    WHERE r.IdRegistro = p_id;
END$$

DELIMITER ;

-- Corregir sp_eliminarimagen
DROP PROCEDURE IF EXISTS sp_eliminarimagen;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_eliminarimagen`(
    IN p_imagen CHAR(18)
)
BEGIN
    -- Eliminar físicamente la imagen de la base de datos
    DELETE FROM tbl_imagenregistro WHERE IdImagen=p_imagen;
    SELECT ROW_COUNT() AS affected;
END$$

DELIMITER ;

-- Corregir sp_exportarregistros
DROP PROCEDURE IF EXISTS sp_exportarregistros;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_exportarregistros`()
BEGIN
    SELECT r.IdRegistro, r.Codigo, DATE(r.FechaInicio) AS Fecha,
           DATE(r.FechaEjecucion) AS FechaEjecucion,
           ar.AreaReportante, ub.Ubicacion,
           r.Descripcion, dt.DescripcionTipo,
           ri.Riesgo, e.Estado, r.Accion,
           ars.AreaResponsable, r.PersonalResponsable,
           r.FechaCreacion
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado=r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante=r.idAreaReportante
    JOIN tbl_arearesponsable ars ON ars.idAreaResponsable=r.idAreaResponsable
    JOIN tbl_ubicacion ub ON ub.idUbicacion=r.idUbicacion
    JOIN tbl_riesgo ri ON ri.IdRiesgo=r.IdRiesgo
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo=r.IdDescripcionTipo
    WHERE r.Archivado=0
    ORDER BY r.FechaCreacion DESC;
END$$

DELIMITER ;

-- Corregir sp_guardarimagen
DROP PROCEDURE IF EXISTS sp_guardarimagen;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_guardarimagen`(
    IN p_id CHAR(18), IN p_registro CHAR(18),
    IN p_usuario_rol CHAR(18), IN p_tipo CHAR(18),
    IN p_estado CHAR(18), IN p_ruta VARCHAR(300),
    IN p_nombre VARCHAR(100), IN p_tamano INT
)
BEGIN
    DECLARE cnt INT;
    SELECT COUNT(*) INTO cnt FROM tbl_imagenregistro
    WHERE IdRegistro=p_registro AND idTipoImagen=p_tipo AND idEstadoImagen != 'EIM003';
    
    IF cnt < 5 THEN
        INSERT INTO tbl_imagenregistro
            (IdImagen,IdRegistro,IdUsuarioRol,idTipoImagen,idEstadoImagen,RutaImagen,NombreArchivo,TamanoKB)
        VALUES (p_id,p_registro,p_usuario_rol,p_tipo,p_estado,p_ruta,p_nombre,p_tamano);
        
        -- Si es imagen de levantamiento (TIM002), cambiar estado a EN PROCESO (EST003)
        IF p_tipo = 'TIM002' THEN
            UPDATE tbl_registro SET idEstado='EST003' WHERE IdRegistro=p_registro;
        END IF;
        
        SELECT 1 AS ok, 'Imagen guardada' AS msg;
    ELSE
        SELECT 0 AS ok, 'Máximo 5 imágenes por tipo' AS msg;
    END IF;
END$$

DELIMITER ;

-- Corregir sp_historialadmin
DROP PROCEDURE IF EXISTS sp_historialadmin;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_historialadmin`()
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.PersonalResponsable, r.FechaArchivado,
           e.Estado,
           ar.AreaReportante, ub.Ubicacion, ri.Riesgo,
           u.NombreCompleto AS Creador,
           ua.NombreCompleto AS Archivador
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_usuarioRol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    LEFT JOIN tbl_usuarioRol ura ON ura.IdUsuarioRol = r.IdUsuarioRolArchivador
    LEFT JOIN tbl_usuario ua ON ua.idUsuario = ura.idUsuario
    WHERE r.Archivado = 1
    ORDER BY r.FechaArchivado DESC;
END$$

DELIMITER ;

-- Corregir sp_historialsupervisor
DROP PROCEDURE IF EXISTS sp_historialsupervisor;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_historialsupervisor`(IN p_usuario_rol CHAR(18))
BEGIN
    SELECT DISTINCT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.PersonalResponsable, r.FechaArchivado,
           e.Estado,
           ar.AreaReportante, ub.Ubicacion, ri.Riesgo,
           u.NombreCompleto AS Creador
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_usuarioRol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    LEFT JOIN tbl_imagenregistro img ON img.IdRegistro = r.IdRegistro AND img.IdUsuarioRol = p_usuario_rol
    WHERE r.Archivado = 1
      AND (img.IdRegistro IS NOT NULL)
    ORDER BY r.FechaArchivado DESC;
END$$

DELIMITER ;

-- Corregir sp_imagenesregistro
DROP PROCEDURE IF EXISTS sp_imagenesregistro;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_imagenesregistro`(IN p_id CHAR(18))
BEGIN
    SELECT i.IdImagen, i.RutaImagen, i.NombreArchivo, i.TamanoKB,
           i.MotivoRechazo, i.FechaSubida, i.FechaRevision,
           ti.TipoImagen, ti.idTipoImagen,
           ei.EstadoImagen, ei.idEstadoImagen,
           u.NombreCompleto AS Subidor
    FROM tbl_imagenregistro i
    JOIN tbl_tipoimagen ti ON ti.idTipoImagen = i.idTipoImagen
    JOIN tbl_estadoImagen ei ON ei.idEstadoImagen = i.idEstadoImagen
    JOIN tbl_usuarioRol ur ON ur.IdUsuarioRol = i.IdUsuarioRol
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    WHERE i.IdRegistro = p_id
    ORDER BY i.FechaSubida;
END$$

DELIMITER ;

-- Corregir sp_leernotificacion
DROP PROCEDURE IF EXISTS sp_leernotificacion;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_leernotificacion`(IN p_id CHAR(18))
BEGIN
    UPDATE tbl_notificacion SET Leida=1 WHERE IdNotificacion=p_id;
END$$

DELIMITER ;

-- Corregir sp_listarregistros
DROP PROCEDURE IF EXISTS sp_listarregistros;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_listarregistros`(IN p_estado VARCHAR(50))
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion, r.PersonalResponsable,
           e.Estado, e.idEstado,
           ar.AreaReportante, ars.AreaResponsable,
           ub.Ubicacion, ri.Riesgo, dt.DescripcionTipo,
           u.NombreCompleto AS Creador,
           (SELECT COUNT(*) FROM tbl_imagenregistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen='TIM001') AS cnt_evidencias,
           (SELECT COUNT(*) FROM tbl_imagenregistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen='TIM002') AS cnt_levantamientos
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_arearesponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN tbl_ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    JOIN tbl_usuarioRol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    WHERE r.Archivado = 0
      AND (p_estado IS NULL OR p_estado = '' OR e.Estado = p_estado)
    ORDER BY r.FechaCreacion DESC;
END$$

DELIMITER ;

-- Corregir sp_listarregistrossupervisor
DROP PROCEDURE IF EXISTS sp_listarregistrossupervisor;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_listarregistrossupervisor`(IN p_estado VARCHAR(50))
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion, r.PersonalResponsable,
           e.Estado, e.idEstado,
           ar.AreaReportante, ars.AreaResponsable,
           ub.Ubicacion, ri.Riesgo, dt.DescripcionTipo,
           u.NombreCompleto AS Creador,
           (SELECT COUNT(*) FROM tbl_imagenregistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen='TIM001') AS cnt_evidencias,
           (SELECT COUNT(*) FROM tbl_imagenregistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen='TIM002') AS cnt_levantamientos
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_arearesponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN tbl_ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    JOIN tbl_usuarioRol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    WHERE r.Archivado = 0
      AND (p_estado IS NULL OR p_estado = '' OR e.Estado = p_estado)
    ORDER BY r.FechaCreacion DESC;
END$$

DELIMITER ;

-- Corregir sp_notificaciones
DROP PROCEDURE IF EXISTS sp_notificaciones;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_notificaciones`(IN p_usuario_rol CHAR(18))
BEGIN
    SELECT IdNotificacion, Mensaje, Leida, Tipo, IdRegistro, FechaCreacion
    FROM tbl_notificacion
    WHERE IdUsuarioRol=p_usuario_rol
    ORDER BY FechaCreacion DESC LIMIT 20;
END$$

DELIMITER ;

-- Corregir sp_siguientecorrelativo
DROP PROCEDURE IF EXISTS sp_siguientecorrelativo;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_siguientecorrelativo`()
BEGIN
    DECLARE v_año VARCHAR(4);
    DECLARE v_num INT;
    SET v_año = YEAR(NOW());
    SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(Codigo,'-',-1) AS UNSIGNED)),0)+1
    INTO v_num FROM tbl_registro
    WHERE YEAR(FechaCreacion)=v_año AND Archivado=0;
    SELECT CONCAT('001-', LPAD(v_num,2,'0')) AS correlativo;
END$$

DELIMITER ;

-- Corregir sp_validarimagen
DROP PROCEDURE IF EXISTS sp_validarimagen;

DELIMITER $$

CREATE DEFINER=`root`@`%` PROCEDURE `sp_validarimagen`(
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

    UPDATE tbl_imagenregistro
    SET idEstadoImagen=v_estado, IdUsuarioRolRevisor=p_revisor,
        FechaRevision=NOW(), MotivoRechazo=IF(p_decision='RECHAZADA',p_comentario,NULL)
    WHERE IdImagen=p_imagen;

    INSERT INTO tbl_historialaprobacion
        (IdHistorial,IdImagen,IdRegistro,IdUsuarioRolRevisor,DecisionTomada,Comentarios)
    VALUES (p_id_historial,p_imagen,p_registro,p_revisor,p_decision,p_comentario);

    -- Si APROBADA: cambiar a COMPLETADO
    IF p_decision = 'APROBADA' THEN
        UPDATE tbl_registro SET idEstado='EST006' WHERE IdRegistro=p_registro;
    ELSE
        -- Si RECHAZADA: volver a PENDIENTE
        UPDATE tbl_registro SET idEstado='EST001' WHERE IdRegistro=p_registro;
    END IF;

    SELECT ROW_COUNT() AS affected;
END$$

DELIMITER ;
