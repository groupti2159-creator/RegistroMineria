-- ============================================================================
-- MEJORAS AL FLUJO DE ESTADOS - DESVIOS SSOMA (VERSIÓN SIMPLIFICADA)
-- ============================================================================

-- 1. CREAR TABLA DE AUDITORÍA DE CAMBIOS DE ESTADO
CREATE TABLE IF NOT EXISTS tbl_auditoria_estado (
    idauditoria INT AUTO_INCREMENT PRIMARY KEY,
    idregistro INT NOT NULL,
    estado_anterior VARCHAR(50),
    estado_nuevo VARCHAR(50) NOT NULL,
    idusuariorol INT,
    comentario TEXT,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idregistro) REFERENCES tbl_registro(idregistro) ON DELETE CASCADE,
    FOREIGN KEY (idusuariorol) REFERENCES tbl_usuariorol(idusuariorol) ON DELETE SET NULL,
    INDEX idx_registro (idregistro),
    INDEX idx_fecha (fecha_cambio)
);

-- 2. CREAR TABLA DE TRANSICIONES VÁLIDAS
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

-- 3. CREAR TABLA DE VALIDACIONES POR ESTADO
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

-- 4. AGREGAR COLUMNAS A tbl_registro SI NO EXISTEN
ALTER TABLE tbl_registro ADD COLUMN estado_anterior VARCHAR(50) AFTER idestado;
ALTER TABLE tbl_registro ADD COLUMN fecha_cambio_estado TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER estado_anterior;
ALTER TABLE tbl_registro ADD COLUMN usuario_cambio_estado INT AFTER fecha_cambio_estado;

-- 5. CREAR ÍNDICES PARA MEJOR RENDIMIENTO
ALTER TABLE tbl_registro ADD INDEX idx_estado (idestado);
ALTER TABLE tbl_registro ADD INDEX idx_fecha_cambio (fecha_cambio_estado);
ALTER TABLE tbl_imagenregistro ADD INDEX idx_estado_imagen (idestadoimagen);
ALTER TABLE tbl_imagenregistro ADD INDEX idx_registro_tipo (idregistro, idtipoimagen);

-- 6. INSERTAR TRANSICIONES VÁLIDAS
INSERT IGNORE INTO tbl_transiciones_estado (estado_origen, estado_destino, requiere_comentario, requiere_validacion, descripcion) VALUES
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

-- 7. INSERTAR VALIDACIONES POR ESTADO
INSERT IGNORE INTO tbl_validaciones_estado (estado, requiere_imagenes_aprobadas, requiere_responsable, requiere_ccta, requiere_descripcion, requiere_accion, min_imagenes, descripcion) VALUES
('Pendiente', FALSE, FALSE, FALSE, TRUE, FALSE, 1, 'Registro creado, mínimo 1 imagen'),
('Asignado', FALSE, TRUE, FALSE, TRUE, FALSE, 1, 'Asignado a responsable'),
('En Proceso', FALSE, TRUE, TRUE, TRUE, FALSE, 1, 'En proceso de resolución'),
('Enviado', FALSE, TRUE, TRUE, TRUE, TRUE, 1, 'Enviado con acción realizada'),
('En Revision', FALSE, TRUE, TRUE, TRUE, TRUE, 1, 'Esperando validación de imágenes'),
('Culminado', TRUE, TRUE, TRUE, TRUE, TRUE, 1, 'Completado con imágenes aprobadas'),
('Rechazado', FALSE, FALSE, FALSE, TRUE, FALSE, 0, 'Rechazado, puede reintentar'),
('Cerrado', FALSE, FALSE, FALSE, TRUE, FALSE, 0, 'Registro cerrado (final)'),
('Atrasado', FALSE, FALSE, FALSE, TRUE, FALSE, 1, 'Registro atrasado');

-- 8. CREAR VISTAS
CREATE OR REPLACE VIEW vw_historial_cambios_estado AS
SELECT 
    a.idauditoria,
    a.idregistro,
    r.codigo,
    a.estado_anterior,
    a.estado_nuevo,
    a.comentario,
    a.fecha_cambio,
    a.idusuariorol AS usuario_cambio,
    ur.idusuariorol
FROM tbl_auditoria_estado a
JOIN tbl_registro r ON a.idregistro = r.idregistro
LEFT JOIN tbl_usuariorol ur ON a.idusuariorol = ur.idusuariorol
ORDER BY a.fecha_cambio DESC;

CREATE OR REPLACE VIEW vw_estado_registro AS
SELECT 
    r.idregistro,
    r.codigo,
    e.estado,
    r.estado_anterior,
    r.fecha_cambio_estado,
    r.usuario_cambio_estado,
    (SELECT COUNT(*) FROM tbl_imagenregistro WHERE idregistro = r.idregistro AND idestadoimagen = 2) AS imagenes_aprobadas,
    (SELECT COUNT(*) FROM tbl_imagenregistro WHERE idregistro = r.idregistro AND idestadoimagen = 1) AS imagenes_pendientes,
    (SELECT COUNT(*) FROM tbl_imagenregistro WHERE idregistro = r.idregistro AND idestadoimagen = 3) AS imagenes_rechazadas
FROM tbl_registro r
JOIN tbl_estado e ON r.idestado = e.idestado;

-- ============================================================================
-- FIN DE MIGRACIONES
-- ============================================================================
