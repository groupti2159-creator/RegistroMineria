-- ============================================================================
-- MEJORAS AL FLUJO DE ESTADOS - DESVIOS SSOMA
-- ============================================================================

-- 1. CREAR TABLA DE AUDITORÍA DE CAMBIOS DE ESTADO
-- ============================================================================
CREATE TABLE IF NOT EXISTS tbl_auditoria_estado (
    idauditoria INT AUTO_INCREMENT PRIMARY KEY,
    idregistro INT NOT NULL,
    estado_anterior VARCHAR(50),
    estado_nuevo VARCHAR(50) NOT NULL,
    idusuariorol INT NOT NULL,
    comentario TEXT,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idregistro) REFERENCES tbl_registro(idregistro) ON DELETE CASCADE,
    FOREIGN KEY (idusuariorol) REFERENCES tbl_usuariorol(idusuariorol) ON DELETE SET NULL,
    INDEX idx_registro (idregistro),
    INDEX idx_fecha (fecha_cambio)
);

-- 2. CREAR TABLA DE TRANSICIONES VÁLIDAS
-- ============================================================================
CREATE TABLE IF NOT EXISTS tbl_transiciones_estado (
    idtransicion INT AUTO_INCREMENT PRIMARY KEY,
    estado_origen VARCHAR(50) NOT NULL,
    estado_destino VARCHAR(50) NOT NULL,
    requiere_comentario BOOLEAN DEFAULT FALSE,
    requiere_validacion BOOLEAN DEFAULT FALSE,
    descripcion VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    UNIQUE KEY unique_transicion (estado_origen, estado_destino),
    INDEX idx_origen (estado_origen)
);

-- 3. INSERTAR TRANSICIONES VÁLIDAS
-- ============================================================================
INSERT INTO tbl_transiciones_estado (estado_origen, estado_destino, requiere_comentario, requiere_validacion, descripcion) VALUES
-- Desde PENDIENTE
('Pendiente', 'Asignado', FALSE, FALSE, 'Asignar a responsable'),
('Pendiente', 'En Proceso', FALSE, FALSE, 'Iniciar proceso directamente'),
('Pendiente', 'Rechazado', TRUE, FALSE, 'Rechazar registro'),
('Pendiente', 'Cerrado', TRUE, FALSE, 'Cerrar sin procesar'),

-- Desde ASIGNADO
('Asignado', 'En Proceso', FALSE, FALSE, 'Iniciar proceso'),
('Asignado', 'Pendiente', FALSE, FALSE, 'Volver a pendiente'),
('Asignado', 'Rechazado', TRUE, FALSE, 'Rechazar'),
('Asignado', 'Cerrado', TRUE, FALSE, 'Cerrar'),

-- Desde EN PROCESO
('En Proceso', 'Enviado', FALSE, FALSE, 'Marcar como enviado'),
('En Proceso', 'Asignado', FALSE, FALSE, 'Volver a asignado'),
('En Proceso', 'Rechazado', TRUE, FALSE, 'Rechazar'),
('En Proceso', 'Cerrado', TRUE, FALSE, 'Cerrar'),

-- Desde ENVIADO
('Enviado', 'En Revision', FALSE, FALSE, 'Iniciar revisión de imágenes'),
('Enviado', 'En Proceso', FALSE, FALSE, 'Volver a proceso'),
('Enviado', 'Rechazado', TRUE, FALSE, 'Rechazar'),
('Enviado', 'Cerrado', TRUE, FALSE, 'Cerrar'),

-- Desde EN REVISIÓN
('En Revision', 'Culminado', FALSE, TRUE, 'Aprobar y culminar'),
('En Revision', 'Rechazado', TRUE, FALSE, 'Rechazar imágenes'),
('En Revision', 'Enviado', FALSE, FALSE, 'Volver a enviado'),

-- Desde CULMINADO
('Culminado', 'Cerrado', FALSE, FALSE, 'Cerrar registro'),
('Culminado', 'En Revision', FALSE, FALSE, 'Volver a revisión'),

-- Desde RECHAZADO
('Rechazado', 'En Proceso', FALSE, FALSE, 'Reintentar'),
('Rechazado', 'Cerrado', FALSE, FALSE, 'Cerrar'),

-- Desde ATRASADO (especial)
('Atrasado', 'En Proceso', FALSE, FALSE, 'Reactivar'),
('Atrasado', 'Cerrado', TRUE, FALSE, 'Cerrar atrasado');

-- 4. CREAR TABLA DE VALIDACIONES POR ESTADO
-- ============================================================================
CREATE TABLE IF NOT EXISTS tbl_validaciones_estado (
    idvalidacion INT AUTO_INCREMENT PRIMARY KEY,
    estado VARCHAR(50) NOT NULL UNIQUE,
    requiere_imagenes_aprobadas BOOLEAN DEFAULT FALSE,
    requiere_responsable BOOLEAN DEFAULT FALSE,
    requiere_ccta BOOLEAN DEFAULT FALSE,
    requiere_descripcion BOOLEAN DEFAULT FALSE,
    requiere_accion BOOLEAN DEFAULT FALSE,
    min_imagenes INT DEFAULT 0,
    descripcion VARCHAR(255)
);

-- 5. INSERTAR VALIDACIONES POR ESTADO
-- ============================================================================
INSERT INTO tbl_validaciones_estado (estado, requiere_imagenes_aprobadas, requiere_responsable, requiere_ccta, requiere_descripcion, requiere_accion, min_imagenes, descripcion) VALUES
('Pendiente', FALSE, FALSE, FALSE, TRUE, FALSE, 1, 'Registro creado, mínimo 1 imagen'),
('Asignado', FALSE, TRUE, FALSE, TRUE, FALSE, 1, 'Asignado a responsable'),
('En Proceso', FALSE, TRUE, TRUE, TRUE, FALSE, 1, 'En proceso de resolución'),
('Enviado', FALSE, TRUE, TRUE, TRUE, TRUE, 1, 'Enviado con acción realizada'),
('En Revision', FALSE, TRUE, TRUE, TRUE, TRUE, 1, 'Esperando validación de imágenes'),
('Culminado', TRUE, TRUE, TRUE, TRUE, TRUE, 1, 'Completado con imágenes aprobadas'),
('Rechazado', FALSE, FALSE, FALSE, TRUE, FALSE, 0, 'Rechazado, puede reintentar'),
('Cerrado', FALSE, FALSE, FALSE, TRUE, FALSE, 0, 'Registro cerrado (final)'),
('Atrasado', FALSE, FALSE, FALSE, TRUE, FALSE, 1, 'Registro atrasado');

-- 6. AGREGAR COLUMNAS A tbl_registro SI NO EXISTEN
-- ============================================================================
ALTER TABLE tbl_registro ADD COLUMN IF NOT EXISTS estado_anterior VARCHAR(50) AFTER idestado;
ALTER TABLE tbl_registro ADD COLUMN IF NOT EXISTS fecha_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER estado_anterior;
ALTER TABLE tbl_registro ADD COLUMN IF NOT EXISTS usuario_cambio_estado INT AFTER fecha_cambio_estado;

-- 7. CREAR ÍNDICES PARA MEJOR RENDIMIENTO
-- ============================================================================
ALTER TABLE tbl_registro ADD INDEX IF NOT EXISTS idx_estado (idestado);
ALTER TABLE tbl_registro ADD INDEX IF NOT EXISTS idx_fecha_cambio (fecha_cambio_estado);
ALTER TABLE tbl_imagenregistro ADD INDEX IF NOT EXISTS idx_estado_imagen (idestadoimagen);
ALTER TABLE tbl_imagenregistro ADD INDEX IF NOT EXISTS idx_registro_tipo (idregistro, idtipoimagen);

-- 8. CREAR PROCEDIMIENTO PARA VALIDAR TRANSICIÓN DE ESTADO
-- ============================================================================
DELIMITER $$

DROP PROCEDURE IF EXISTS sp_validar_transicion_estado$$

CREATE PROCEDURE sp_validar_transicion_estado(
    IN p_idregistro INT,
    IN p_estado_nuevo VARCHAR(50),
    OUT p_valido BOOLEAN,
    OUT p_mensaje VARCHAR(500)
)
BEGIN
    DECLARE v_estado_actual VARCHAR(50);
    DECLARE v_transicion_existe INT;
    DECLARE v_requiere_comentario BOOLEAN;
    DECLARE v_requiere_validacion BOOLEAN;
    DECLARE v_imagenes_aprobadas INT;
    DECLARE v_imagenes_pendientes INT;
    DECLARE v_responsable INT;
    DECLARE v_ccta INT;
    DECLARE v_descripcion TEXT;
    DECLARE v_accion TEXT;
    
    -- Obtener estado actual
    SELECT idestado INTO v_estado_actual FROM tbl_registro WHERE idregistro = p_idregistro;
    
    IF v_estado_actual IS NULL THEN
        SET p_valido = FALSE;
        SET p_mensaje = 'Registro no encontrado';
        LEAVE;
    END IF;
    
    -- Verificar si la transición existe
    SELECT COUNT(*) INTO v_transicion_existe 
    FROM tbl_transiciones_estado 
    WHERE estado_origen = v_estado_actual 
    AND estado_destino = p_estado_nuevo 
    AND activo = TRUE;
    
    IF v_transicion_existe = 0 THEN
        SET p_valido = FALSE;
        SET p_mensaje = CONCAT('Transición no permitida: ', v_estado_actual, ' → ', p_estado_nuevo);
        LEAVE;
    END IF;
    
    -- Obtener requisitos de la transición
    SELECT requiere_comentario, requiere_validacion 
    INTO v_requiere_comentario, v_requiere_validacion
    FROM tbl_transiciones_estado 
    WHERE estado_origen = v_estado_actual 
    AND estado_destino = p_estado_nuevo;
    
    -- Validar requisitos del estado destino
    SELECT 
        requiere_imagenes_aprobadas,
        requiere_responsable,
        requiere_ccta,
        requiere_descripcion,
        requiere_accion
    INTO 
        v_imagenes_aprobadas,
        v_responsable,
        v_ccta,
        v_descripcion,
        v_accion
    FROM tbl_validaciones_estado 
    WHERE estado = p_estado_nuevo;
    
    -- Obtener datos del registro
    SELECT 
        idpersonalresponsable,
        idcctaresponsable,
        descripcion,
        accion
    INTO 
        v_responsable,
        v_ccta,
        v_descripcion,
        v_accion
    FROM tbl_registro 
    WHERE idregistro = p_idregistro;
    
    -- Validar imágenes aprobadas si es requerido
    IF v_imagenes_aprobadas THEN
        SELECT COUNT(*) INTO v_imagenes_aprobadas 
        FROM tbl_imagenregistro 
        WHERE idregistro = p_idregistro 
        AND idestadoimagen = 2;
        
        IF v_imagenes_aprobadas = 0 THEN
            SET p_valido = FALSE;
            SET p_mensaje = 'Se requiere al menos 1 imagen aprobada para este estado';
            LEAVE;
        END IF;
    END IF;
    
    -- Validar responsable si es requerido
    IF v_responsable AND v_responsable IS NULL THEN
        SET p_valido = FALSE;
        SET p_mensaje = 'Se requiere asignar un responsable para este estado';
        LEAVE;
    END IF;
    
    -- Validar CCTA si es requerido
    IF v_ccta AND v_ccta IS NULL THEN
        SET p_valido = FALSE;
        SET p_mensaje = 'Se requiere asignar un CCTA responsable para este estado';
        LEAVE;
    END IF;
    
    -- Validar descripción si es requerida
    IF v_descripcion AND (v_descripcion IS NULL OR v_descripcion = '') THEN
        SET p_valido = FALSE;
        SET p_mensaje = 'Se requiere una descripción para este estado';
        LEAVE;
    END IF;
    
    -- Validar acción si es requerida
    IF v_accion AND (v_accion IS NULL OR v_accion = '') THEN
        SET p_valido = FALSE;
        SET p_mensaje = 'Se requiere describir la acción realizada para este estado';
        LEAVE;
    END IF;
    
    -- Si llegamos aquí, la transición es válida
    SET p_valido = TRUE;
    SET p_mensaje = 'Transición válida';
END$$

DELIMITER ;

-- 9. CREAR PROCEDIMIENTO PARA CAMBIAR ESTADO CON AUDITORÍA
-- ============================================================================
DELIMITER $$

DROP PROCEDURE IF EXISTS sp_cambiar_estado_registro$$

CREATE PROCEDURE sp_cambiar_estado_registro(
    IN p_idregistro INT,
    IN p_estado_nuevo VARCHAR(50),
    IN p_idusuariorol INT,
    IN p_comentario TEXT,
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500)
)
BEGIN
    DECLARE v_estado_actual VARCHAR(50);
    DECLARE v_valido BOOLEAN;
    DECLARE v_mensaje_validacion VARCHAR(500);
    
    -- Obtener estado actual
    SELECT idestado INTO v_estado_actual FROM tbl_registro WHERE idregistro = p_idregistro;
    
    -- Validar transición
    CALL sp_validar_transicion_estado(p_idregistro, p_estado_nuevo, v_valido, v_mensaje_validacion);
    
    IF NOT v_valido THEN
        SET p_exito = FALSE;
        SET p_mensaje = v_mensaje_validacion;
        LEAVE;
    END IF;
    
    -- Actualizar estado del registro
    UPDATE tbl_registro 
    SET 
        idestado = (SELECT idestado FROM tbl_estado WHERE estado = p_estado_nuevo LIMIT 1),
        estado_anterior = v_estado_actual,
        fecha_cambio_estado = NOW(),
        usuario_cambio_estado = p_idusuariorol
    WHERE idregistro = p_idregistro;
    
    -- Registrar en auditoría
    INSERT INTO tbl_auditoria_estado (idregistro, estado_anterior, estado_nuevo, idusuariorol, comentario)
    VALUES (p_idregistro, v_estado_actual, p_estado_nuevo, p_idusuariorol, p_comentario);
    
    SET p_exito = TRUE;
    SET p_mensaje = CONCAT('Estado cambiado de ', v_estado_actual, ' a ', p_estado_nuevo);
END$$

DELIMITER ;

-- 10. CREAR PROCEDIMIENTO PARA CAMBIAR ESTADO AUTOMÁTICAMENTE
-- ============================================================================
DELIMITER $$

DROP PROCEDURE IF EXISTS sp_cambiar_estado_automatico$$

CREATE PROCEDURE sp_cambiar_estado_automatico(
    IN p_idregistro INT,
    IN p_evento VARCHAR(50),
    OUT p_exito BOOLEAN,
    OUT p_mensaje VARCHAR(500)
)
BEGIN
    DECLARE v_estado_actual VARCHAR(50);
    DECLARE v_estado_nuevo VARCHAR(50);
    
    -- Obtener estado actual
    SELECT idestado INTO v_estado_actual FROM tbl_registro WHERE idregistro = p_idregistro;
    
    -- Determinar nuevo estado según el evento
    CASE p_evento
        WHEN 'supervisor_sube_imagenes' THEN
            IF v_estado_actual = 'Enviado' THEN
                SET v_estado_nuevo = 'En Revision';
            END IF;
        WHEN 'admin_aprueba_imagenes' THEN
            IF v_estado_actual = 'En Revision' THEN
                SET v_estado_nuevo = 'Culminado';
            END IF;
        WHEN 'admin_rechaza_imagenes' THEN
            IF v_estado_actual = 'En Revision' THEN
                SET v_estado_nuevo = 'Rechazado';
            END IF;
    END CASE;
    
    -- Si hay nuevo estado, cambiar
    IF v_estado_nuevo IS NOT NULL AND v_estado_nuevo != v_estado_actual THEN
        UPDATE tbl_registro 
        SET 
            idestado = (SELECT idestado FROM tbl_estado WHERE estado = v_estado_nuevo LIMIT 1),
            estado_anterior = v_estado_actual,
            fecha_cambio_estado = NOW(),
            usuario_cambio_estado = 1
        WHERE idregistro = p_idregistro;
        
        INSERT INTO tbl_auditoria_estado (idregistro, estado_anterior, estado_nuevo, idusuariorol, comentario)
        VALUES (p_idregistro, v_estado_actual, v_estado_nuevo, 1, CONCAT('Cambio automático por evento: ', p_evento));
        
        SET p_exito = TRUE;
        SET p_mensaje = CONCAT('Estado cambiado automáticamente a ', v_estado_nuevo);
    ELSE
        SET p_exito = FALSE;
        SET p_mensaje = 'No hay cambio de estado para este evento';
    END IF;
END$$

DELIMITER ;

-- 11. CREAR VISTA PARA VER HISTORIAL DE CAMBIOS
-- ============================================================================
CREATE OR REPLACE VIEW vw_historial_cambios_estado AS
SELECT 
    a.idauditoria,
    a.idregistro,
    r.codigo,
    a.estado_anterior,
    a.estado_nuevo,
    a.comentario,
    a.fecha_cambio,
    CONCAT(u.nombre, ' ', u.apellido) AS usuario_cambio,
    ur.idusuariorol
FROM tbl_auditoria_estado a
JOIN tbl_registro r ON a.idregistro = r.idregistro
LEFT JOIN tbl_usuariorol ur ON a.idusuariorol = ur.idusuariorol
LEFT JOIN tbl_usuario u ON ur.idusuario = u.idusuario
ORDER BY a.fecha_cambio DESC;

-- 12. CREAR VISTA PARA VALIDAR ESTADO ACTUAL
-- ============================================================================
CREATE OR REPLACE VIEW vw_estado_registro AS
SELECT 
    r.idregistro,
    r.codigo,
    e.estado,
    r.estado_anterior,
    r.fecha_cambio_estado,
    CONCAT(u.nombre, ' ', u.apellido) AS usuario_cambio,
    (SELECT COUNT(*) FROM tbl_imagenregistro WHERE idregistro = r.idregistro AND idestadoimagen = 2) AS imagenes_aprobadas,
    (SELECT COUNT(*) FROM tbl_imagenregistro WHERE idregistro = r.idregistro AND idestadoimagen = 1) AS imagenes_pendientes,
    (SELECT COUNT(*) FROM tbl_imagenregistro WHERE idregistro = r.idregistro AND idestadoimagen = 3) AS imagenes_rechazadas
FROM tbl_registro r
JOIN tbl_estado e ON r.idestado = e.idestado
LEFT JOIN tbl_usuariorol ur ON r.usuario_cambio_estado = ur.idusuariorol
LEFT JOIN tbl_usuario u ON ur.idusuario = u.idusuario;

-- ============================================================================
-- FIN DE MIGRACIONES
-- ============================================================================
