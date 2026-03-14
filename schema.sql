-- ============================================================
--  DESVÍOS AMBIENTALES — MySQL Schema COMPLETO
--  Con Stored Procedures y tabla de historial
-- ============================================================

CREATE DATABASE IF NOT EXISTS desvios_ambientales
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE desvios_ambientales;

-- ─── TABLAS MAESTRAS ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS Tbl_Roles (
    idRoles     CHAR(18) PRIMARY KEY,
    NombreRol   VARCHAR(50) NOT NULL,
    Descripcion VARCHAR(200)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_Estado (
    idEstado    CHAR(18) PRIMARY KEY,
    Estado      VARCHAR(50) NOT NULL,
    Descripcion VARCHAR(200),
    Orden       INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_Riesgo (
    IdRiesgo CHAR(18) PRIMARY KEY,
    Riesgo   VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_DescripcionTipo (
    IdDescripcionTipo CHAR(18) PRIMARY KEY,
    DescripcionTipo   VARCHAR(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_AreaReportante (
    idAreaReportante CHAR(18) PRIMARY KEY,
    AreaReportante   VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_AreaResponsable (
    idAreaResponsable CHAR(18) PRIMARY KEY,
    AreaResponsable   VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_Ubicacion (
    idUbicacion CHAR(18) PRIMARY KEY,
    Ubicacion   VARCHAR(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_EstadoImagen (
    idEstadoImagen CHAR(18) PRIMARY KEY,
    EstadoImagen   VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_TipoImagen (
    idTipoImagen CHAR(18) PRIMARY KEY,
    TipoImagen   VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── USUARIOS ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS Tbl_Usuario (
    idUsuario      CHAR(18) PRIMARY KEY,
    DNI            VARCHAR(20) NOT NULL UNIQUE,
    NombreCompleto VARCHAR(100) NOT NULL,
    Correo         VARCHAR(100),
    Contrasena     VARCHAR(255) NOT NULL,
    Activo         TINYINT(1) DEFAULT 1,
    FechaCreacion  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_UsuarioRol (
    IdUsuarioRol    CHAR(18) PRIMARY KEY,
    idUsuario       CHAR(18) NOT NULL,
    idRoles         CHAR(18) NOT NULL,
    FechaAsignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idUsuario) REFERENCES Tbl_Usuario(idUsuario) ON DELETE CASCADE,
    FOREIGN KEY (idRoles)   REFERENCES Tbl_Roles(idRoles)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── REGISTRO PRINCIPAL ──────────────────────────────────────

CREATE TABLE IF NOT EXISTS Tbl_Registro (
    IdRegistro          CHAR(18) PRIMARY KEY,
    Codigo              VARCHAR(20),
    FechaInicio         DATETIME NOT NULL,
    FechaEjecucion      DATETIME,
    Descripcion         VARCHAR(500) NOT NULL,
    Accion              VARCHAR(300),
    NotasLevantamiento  TEXT,
    idAreaReportante    CHAR(18) NOT NULL,
    idAreaResponsable   CHAR(18) NOT NULL,
    idUbicacion         CHAR(18) NOT NULL,
    IdRiesgo            CHAR(18) NOT NULL,
    IdDescripcionTipo   CHAR(18) NOT NULL,
    idEstado            CHAR(18) NOT NULL,
    IdUsuarioRolCreador CHAR(18) NOT NULL,
    PersonalResponsable VARCHAR(100),
    CctaResponsable     CHAR(18) NULL,
    Archivado           TINYINT(1) DEFAULT 0,
    FechaArchivado      DATETIME NULL,
    IdUsuarioRolArchivador CHAR(18) NULL,
    FechaCreacion       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FechaActualizacion  DATETIME ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (idAreaReportante)  REFERENCES Tbl_AreaReportante(idAreaReportante),
    FOREIGN KEY (idAreaResponsable) REFERENCES Tbl_AreaResponsable(idAreaResponsable),
    FOREIGN KEY (idUbicacion)       REFERENCES Tbl_Ubicacion(idUbicacion),
    FOREIGN KEY (IdRiesgo)          REFERENCES Tbl_Riesgo(IdRiesgo),
    FOREIGN KEY (IdDescripcionTipo) REFERENCES Tbl_DescripcionTipo(IdDescripcionTipo),
    FOREIGN KEY (idEstado)          REFERENCES Tbl_Estado(idEstado),
    FOREIGN KEY (IdUsuarioRolCreador) REFERENCES Tbl_UsuarioRol(IdUsuarioRol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── ASIGNACIÓN ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS Tbl_Asignacion (
    IdAsignacion          CHAR(18) PRIMARY KEY,
    IdRegistro            CHAR(18) NOT NULL,
    IdUsuarioRolAsignado  CHAR(18) NOT NULL,
    IdUsuarioRolAsignador CHAR(18) NOT NULL,
    RolContexto           VARCHAR(20) NOT NULL,
    Instrucciones         VARCHAR(300),
    Activa                TINYINT(1) DEFAULT 1,
    FechaAsignacion       DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdRegistro)            REFERENCES Tbl_Registro(IdRegistro) ON DELETE CASCADE,
    FOREIGN KEY (IdUsuarioRolAsignado)  REFERENCES Tbl_UsuarioRol(IdUsuarioRol),
    FOREIGN KEY (IdUsuarioRolAsignador) REFERENCES Tbl_UsuarioRol(IdUsuarioRol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── IMÁGENES ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS Tbl_ImagenRegistro (
    IdImagen            CHAR(18) PRIMARY KEY,
    IdRegistro          CHAR(18) NOT NULL,
    IdUsuarioRol        CHAR(18) NOT NULL,
    idTipoImagen        CHAR(18) NOT NULL,
    idEstadoImagen      CHAR(18) NOT NULL,
    RutaImagen          VARCHAR(300) NOT NULL,
    NombreArchivo       VARCHAR(100),
    TamanoKB            INT,
    MotivoRechazo       VARCHAR(300),
    IdUsuarioRolRevisor CHAR(18),
    FechaRevision       DATETIME,
    FechaSubida         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdRegistro)     REFERENCES Tbl_Registro(IdRegistro) ON DELETE CASCADE,
    FOREIGN KEY (IdUsuarioRol)   REFERENCES Tbl_UsuarioRol(IdUsuarioRol),
    FOREIGN KEY (idTipoImagen)   REFERENCES Tbl_TipoImagen(idTipoImagen),
    FOREIGN KEY (idEstadoImagen) REFERENCES Tbl_EstadoImagen(idEstadoImagen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── HISTORIAL APROBACIÓN ────────────────────────────────────

CREATE TABLE IF NOT EXISTS Tbl_HistorialAprobacion (
    IdHistorial           CHAR(18) PRIMARY KEY,
    IdImagen              CHAR(18) NOT NULL,
    IdRegistro            CHAR(18) NOT NULL,
    IdUsuarioRolRevisor   CHAR(18) NOT NULL,
    DecisionTomada        VARCHAR(20) NOT NULL,
    Comentarios           VARCHAR(300),
    FechaDecision         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdImagen)            REFERENCES Tbl_ImagenRegistro(IdImagen),
    FOREIGN KEY (IdRegistro)          REFERENCES Tbl_Registro(IdRegistro),
    FOREIGN KEY (IdUsuarioRolRevisor) REFERENCES Tbl_UsuarioRol(IdUsuarioRol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── NOTIFICACIONES ──────────────────────────────────────────

CREATE TABLE IF NOT EXISTS Tbl_Notificacion (
    IdNotificacion CHAR(18) PRIMARY KEY,
    IdUsuarioRol   CHAR(18) NOT NULL,
    Mensaje        VARCHAR(300) NOT NULL,
    Leida          TINYINT(1) DEFAULT 0,
    Tipo           VARCHAR(20) DEFAULT 'info',
    IdRegistro     CHAR(18),
    FechaCreacion  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdUsuarioRol) REFERENCES Tbl_UsuarioRol(IdUsuarioRol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── DATOS INICIALES ─────────────────────────────────────────

INSERT IGNORE INTO Tbl_Roles VALUES
('ROL001','Administrador','Crea y aprueba registros'),
('ROL002','Supervisor','Supervisa y valida'),
('ROL003','Trabajador','Resuelve registros asignados');

INSERT IGNORE INTO Tbl_Estado VALUES
('EST001','Pendiente',   'Sin asignar',1),
('EST002','Asignado',    'Asignado al personal',2),
('EST003','En Proceso',  'Trabajando',3),
('EST004','Enviado',     'Trabajador subió imagen',4),
('EST005','En Revisión', 'Supervisor validó',5),
('EST006','Culminado',   'Aprobado por admin',6),
('EST007','Rechazado',   'Rechazado, reintentar',7),
('EST008','Cerrado',     'Cerrado',8);

INSERT IGNORE INTO Tbl_Riesgo VALUES
('RIE001','Bajo'),('RIE002','Medio'),('RIE003','Alto'),('RIE004','Crítico');

INSERT IGNORE INTO Tbl_DescripcionTipo VALUES
('TIP001','Incumplimiento de IGA'),
('TIP002','Riesgo Eléctrico'),
('TIP003','Riesgo Civil'),
('TIP004','Riesgo Mecánico'),
('TIP005','Seguridad Industrial'),
('TIP006','Ambiental'),
('TIP007','POLVO'),
('TIP008','DISPOSICIÓN RESIDUOS PELIGROSOS');

INSERT IGNORE INTO Tbl_AreaReportante VALUES
('ARE001','Los Andes'),('ARE002','Operaciones'),
('ARE003','Mantenimiento'),('ARE004','Seguridad'),
('ARE005','Geología'),('ARE006','Medio Ambiente');

INSERT IGNORE INTO Tbl_AreaResponsable VALUES
('ARS001','Proyectos'),('ARS002','Mantenimiento General'),
('ARS003','Ingeniería'),('ARS004','Seguridad Industrial'),
('ARS005','Geología'),('ARS006','Medio Ambiente');

INSERT IGNORE INTO Tbl_Ubicacion VALUES
('UBI001','Zona I - NORTE - Sector A'),
('UBI002','Zona II - Mascota - Bodega Pique Central'),
('UBI003','Zona III - Sur - Sector B'),
('UBI004','Patio Exterior'),
('UBI005','Almacén Central'),
('UBI006','Zona I - OESTE - Planta de Procesamiento');

INSERT IGNORE INTO Tbl_EstadoImagen VALUES
('EIM001','Pendiente'),('EIM002','Aprobada'),('EIM003','Rechazada');

INSERT IGNORE INTO Tbl_TipoImagen VALUES
('TIM001','ImagenError'),
('TIM002','ImagenLevantamiento'),
('TIM003','ImagenValidacion');

INSERT IGNORE INTO Tbl_Usuario VALUES
('USR001','12345678','Eco Supervisor','admin@eco.com',   MD5('admin123'),1,NOW()),
('USR002','87654321','Juan Supervisor','sup@eco.com',    MD5('sup123'),  1,NOW()),
('USR003','11223344','Carlos Trabajador','trab@eco.com', MD5('trab123'), 1,NOW());

INSERT IGNORE INTO Tbl_UsuarioRol VALUES
('UR001','USR001','ROL001',NOW()),
('UR002','USR002','ROL002',NOW()),
('UR003','USR003','ROL003',NOW());

-- ═══════════════════════════════════════════════════════════
--  STORED PROCEDURES
-- ═══════════════════════════════════════════════════════════

DELIMITER $$

-- SP: Login
DROP PROCEDURE IF EXISTS SP_Login$$
CREATE PROCEDURE SP_Login(IN p_dni VARCHAR(20), IN p_pass VARCHAR(255))
BEGIN
    SELECT u.idUsuario, u.DNI, u.NombreCompleto, u.Correo, u.Activo,
           ur.IdUsuarioRol, r.idRoles, r.NombreRol
    FROM Tbl_Usuario u
    JOIN Tbl_UsuarioRol ur ON ur.idUsuario = u.idUsuario
    JOIN Tbl_Roles r ON r.idRoles = ur.idRoles
    WHERE u.DNI = p_dni AND u.Contrasena = MD5(p_pass) AND u.Activo = 1
    LIMIT 1;
END$$

-- SP: Dashboard stats
DROP PROCEDURE IF EXISTS SP_DashboardStats$$
CREATE PROCEDURE SP_DashboardStats()
BEGIN
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN e.Estado = 'Culminado' THEN 1 ELSE 0 END) AS culminados,
        SUM(CASE WHEN e.Estado IN ('En Proceso','Enviado','En Revisión') THEN 1 ELSE 0 END) AS en_proceso,
        SUM(CASE WHEN e.Estado = 'Pendiente' THEN 1 ELSE 0 END) AS pendientes
    FROM Tbl_Registro r
    JOIN Tbl_Estado e ON e.idEstado = r.idEstado
    WHERE r.Archivado = 0;
END$$

-- SP: Listar registros para admin
DROP PROCEDURE IF EXISTS SP_ListarRegistros$$
CREATE PROCEDURE SP_ListarRegistros(IN p_estado VARCHAR(50))
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion, r.PersonalResponsable,
           arc.AreaReportante AS CctaResponsable,
           e.Estado, e.idEstado,
           ar.AreaReportante, ars.AreaResponsable,
           ub.Ubicacion, ri.Riesgo, dt.DescripcionTipo,
           u.NombreCompleto AS Creador,
           (SELECT COUNT(*) FROM Tbl_ImagenRegistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen='TIM001') AS cnt_evidencias,
           (SELECT COUNT(*) FROM Tbl_ImagenRegistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen='TIM002') AS cnt_levantamientos
    FROM Tbl_Registro r
    JOIN Tbl_Estado e ON e.idEstado = r.idEstado
    JOIN Tbl_AreaReportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN Tbl_AreaResponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN Tbl_Ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN Tbl_Riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN Tbl_DescripcionTipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    JOIN Tbl_UsuarioRol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN Tbl_Usuario u ON u.idUsuario = ur.idUsuario
    WHERE r.Archivado = 0
      AND (p_estado IS NULL OR p_estado = '' OR e.Estado = p_estado)
    ORDER BY r.FechaCreacion DESC;
END$$

-- SP: Listar registros para supervisor/trabajador
DROP PROCEDURE IF EXISTS SP_ListarRegistrosSupervisor$$
CREATE PROCEDURE SP_ListarRegistrosSupervisor(IN p_estado VARCHAR(50))
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion, r.PersonalResponsable,
           e.Estado, e.idEstado,
           ar.AreaReportante, ars.AreaResponsable,
           ub.Ubicacion, ri.Riesgo, dt.DescripcionTipo,
           u.NombreCompleto AS Creador,
           (SELECT COUNT(*) FROM Tbl_ImagenRegistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen='TIM001') AS cnt_evidencias,
           (SELECT COUNT(*) FROM Tbl_ImagenRegistro img WHERE img.IdRegistro = r.IdRegistro AND img.idTipoImagen='TIM002') AS cnt_levantamientos
    FROM Tbl_Registro r
    JOIN Tbl_Estado e ON e.idEstado = r.idEstado
    JOIN Tbl_AreaReportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN Tbl_AreaResponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN Tbl_Ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN Tbl_Riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN Tbl_DescripcionTipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    JOIN Tbl_UsuarioRol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN Tbl_Usuario u ON u.idUsuario = ur.idUsuario
    WHERE r.Archivado = 0
      AND (p_estado IS NULL OR p_estado = '' OR e.Estado = p_estado)
    ORDER BY r.FechaCreacion DESC;
END$$

-- SP: Detalle de un registro
DROP PROCEDURE IF EXISTS SP_DetalleRegistro$$
CREATE PROCEDURE SP_DetalleRegistro(IN p_id CHAR(18))
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
    FROM Tbl_Registro r
    JOIN Tbl_Estado e ON e.idEstado = r.idEstado
    JOIN Tbl_AreaReportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN Tbl_AreaResponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
    JOIN Tbl_Ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN Tbl_Riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN Tbl_DescripcionTipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
    JOIN Tbl_UsuarioRol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN Tbl_Usuario u ON u.idUsuario = ur.idUsuario
    WHERE r.IdRegistro = p_id;
END$$

-- SP: Imagenes de un registro
DROP PROCEDURE IF EXISTS SP_ImagenesRegistro$$
CREATE PROCEDURE SP_ImagenesRegistro(IN p_id CHAR(18))
BEGIN
    SELECT i.IdImagen, i.RutaImagen, i.NombreArchivo, i.TamanoKB,
           i.MotivoRechazo, i.FechaSubida, i.FechaRevision,
           ti.TipoImagen, ti.idTipoImagen,
           ei.EstadoImagen, ei.idEstadoImagen,
           u.NombreCompleto AS Subidor
    FROM Tbl_ImagenRegistro i
    JOIN Tbl_TipoImagen ti ON ti.idTipoImagen = i.idTipoImagen
    JOIN Tbl_EstadoImagen ei ON ei.idEstadoImagen = i.idEstadoImagen
    JOIN Tbl_UsuarioRol ur ON ur.IdUsuarioRol = i.IdUsuarioRol
    JOIN Tbl_Usuario u ON u.idUsuario = ur.idUsuario
    WHERE i.IdRegistro = p_id
      AND i.idEstadoImagen != 'EIM003'
    ORDER BY i.FechaSubida;
END$$

-- SP: Crear registro
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
    INSERT INTO Tbl_Registro (
        IdRegistro, Codigo, FechaInicio, FechaEjecucion, Descripcion, Accion,
        idAreaReportante, idAreaResponsable, idUbicacion, IdRiesgo,
        IdDescripcionTipo, idEstado, IdUsuarioRolCreador,
        PersonalResponsable, CctaResponsable
    ) VALUES (
        p_id, p_codigo, p_fecha, p_fecha_ejec, p_desc, p_accion,
        p_area_rep, p_area_res, p_ubic, p_riesgo,
        p_tipo, p_estado, p_creador, p_personal, p_ccta
    );
    SELECT ROW_COUNT() AS affected;
END$$

-- SP: Actualizar registro
DROP PROCEDURE IF EXISTS SP_ActualizarRegistro$$
CREATE PROCEDURE SP_ActualizarRegistro(
    IN p_id CHAR(18), IN p_fecha DATETIME, IN p_fecha_ejec DATETIME,
    IN p_desc VARCHAR(500), IN p_accion VARCHAR(300),
    IN p_area_rep CHAR(18), IN p_area_res CHAR(18),
    IN p_ubic CHAR(18), IN p_riesgo CHAR(18),
    IN p_tipo CHAR(18), IN p_estado CHAR(18),
    IN p_personal VARCHAR(100), IN p_ccta VARCHAR(100)
)
BEGIN
    UPDATE Tbl_Registro SET
        FechaInicio=p_fecha, FechaEjecucion=p_fecha_ejec,
        Descripcion=p_desc, Accion=p_accion,
        idAreaReportante=p_area_rep, idAreaResponsable=p_area_res,
        idUbicacion=p_ubic, IdRiesgo=p_riesgo,
        IdDescripcionTipo=p_tipo, idEstado=p_estado,
        PersonalResponsable=p_personal, CctaResponsable=p_ccta
    WHERE IdRegistro=p_id;
    SELECT ROW_COUNT() AS affected;
END$$

-- SP: Archivar registro (admin)
DROP PROCEDURE IF EXISTS SP_ArchivarRegistro$$
CREATE PROCEDURE SP_ArchivarRegistro(IN p_id CHAR(18), IN p_archivador CHAR(18))
BEGIN
    UPDATE Tbl_Registro
    SET Archivado=1, FechaArchivado=NOW(), IdUsuarioRolArchivador=p_archivador
    WHERE IdRegistro=p_id AND idEstado='EST006';
    SELECT ROW_COUNT() AS affected;
END$$

-- SP: Historial admin (todos los archivados)
DROP PROCEDURE IF EXISTS SP_HistorialAdmin$$
CREATE PROCEDURE SP_HistorialAdmin()
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.PersonalResponsable, r.FechaArchivado,
           e.Estado,
           ar.AreaReportante, ub.Ubicacion, ri.Riesgo,
           u.NombreCompleto AS Creador,
           ua.NombreCompleto AS Archivador
    FROM Tbl_Registro r
    JOIN Tbl_Estado e ON e.idEstado = r.idEstado
    JOIN Tbl_AreaReportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN Tbl_Ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN Tbl_Riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN Tbl_UsuarioRol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN Tbl_Usuario u ON u.idUsuario = ur.idUsuario
    LEFT JOIN Tbl_UsuarioRol ura ON ura.IdUsuarioRol = r.IdUsuarioRolArchivador
    LEFT JOIN Tbl_Usuario ua ON ua.idUsuario = ura.idUsuario
    WHERE r.Archivado = 1
    ORDER BY r.FechaArchivado DESC;
END$$

-- SP: Historial supervisor/trabajador (sus registros archivados donde participó)
DROP PROCEDURE IF EXISTS SP_HistorialSupervisor$$
CREATE PROCEDURE SP_HistorialSupervisor(IN p_usuario_rol CHAR(18))
BEGIN
    SELECT DISTINCT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.PersonalResponsable, r.FechaArchivado,
           e.Estado,
           ar.AreaReportante, ub.Ubicacion, ri.Riesgo,
           u.NombreCompleto AS Creador
    FROM Tbl_Registro r
    JOIN Tbl_Estado e ON e.idEstado = r.idEstado
    JOIN Tbl_AreaReportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN Tbl_Ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN Tbl_Riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN Tbl_UsuarioRol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN Tbl_Usuario u ON u.idUsuario = ur.idUsuario
    LEFT JOIN Tbl_ImagenRegistro img ON img.IdRegistro = r.IdRegistro AND img.IdUsuarioRol = p_usuario_rol
    WHERE r.Archivado = 1
      AND (img.IdRegistro IS NOT NULL)
    ORDER BY r.FechaArchivado DESC;
END$$

-- SP: Guardar imagen
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
    WHERE IdRegistro=p_registro AND idTipoImagen=p_tipo;
    IF cnt < 5 THEN
        INSERT INTO Tbl_ImagenRegistro
            (IdImagen,IdRegistro,IdUsuarioRol,idTipoImagen,idEstadoImagen,RutaImagen,NombreArchivo,TamanoKB)
        VALUES (p_id,p_registro,p_usuario_rol,p_tipo,p_estado,p_ruta,p_nombre,p_tamano);
        SELECT 1 AS ok, 'Imagen guardada' AS msg;
    ELSE
        SELECT 0 AS ok, 'Máximo 5 imágenes por tipo' AS msg;
    END IF;
END$$

-- SP: Cambiar estado registro
DROP PROCEDURE IF EXISTS SP_CambiarEstado$$
CREATE PROCEDURE SP_CambiarEstado(IN p_id CHAR(18), IN p_estado CHAR(18))
BEGIN
    UPDATE Tbl_Registro SET idEstado=p_estado WHERE IdRegistro=p_id;
    SELECT ROW_COUNT() AS affected;
END$$

-- SP: Validar imagen (admin aprueba/rechaza)
DROP PROCEDURE IF EXISTS SP_ValidarImagen$$
CREATE PROCEDURE SP_ValidarImagen(
    IN p_id_historial CHAR(18), IN p_imagen CHAR(18), IN p_registro CHAR(18),
    IN p_revisor CHAR(18), IN p_decision VARCHAR(20),
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

    -- Si APROBADA: verificar si todas las imágenes NO rechazadas están aprobadas -> COMPLETADO
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
        -- Si RECHAZADA: volver a PENDIENTE
        UPDATE Tbl_Registro SET idEstado='EST001' WHERE IdRegistro=p_registro;
    END IF;

    SELECT ROW_COUNT() AS affected;
END$$

-- SP: Crear notificación
DROP PROCEDURE IF EXISTS SP_CrearNotificacion$$
CREATE PROCEDURE SP_CrearNotificacion(
    IN p_id CHAR(18), IN p_usuario_rol CHAR(18),
    IN p_mensaje VARCHAR(300), IN p_tipo VARCHAR(20),
    IN p_registro CHAR(18)
)
BEGIN
    INSERT INTO Tbl_Notificacion(IdNotificacion,IdUsuarioRol,Mensaje,Tipo,IdRegistro)
    VALUES(p_id,p_usuario_rol,p_mensaje,p_tipo,p_registro);
END$$

-- SP: Notificaciones del usuario
DROP PROCEDURE IF EXISTS SP_Notificaciones$$
CREATE PROCEDURE SP_Notificaciones(IN p_usuario_rol CHAR(18))
BEGIN
    SELECT IdNotificacion, Mensaje, Leida, Tipo, IdRegistro, FechaCreacion
    FROM Tbl_Notificacion
    WHERE IdUsuarioRol=p_usuario_rol
    ORDER BY FechaCreacion DESC LIMIT 20;
END$$

-- SP: Marcar notificacion leida
DROP PROCEDURE IF EXISTS SP_LeerNotificacion$$
CREATE PROCEDURE SP_LeerNotificacion(IN p_id CHAR(18))
BEGIN
    UPDATE Tbl_Notificacion SET Leida=1 WHERE IdNotificacion=p_id;
END$$

-- SP: Contar notificaciones no leídas
DROP PROCEDURE IF EXISTS SP_ContarNotificaciones$$
CREATE PROCEDURE SP_ContarNotificaciones(IN p_usuario_rol CHAR(18))
BEGIN
    SELECT COUNT(*) AS total FROM Tbl_Notificacion
    WHERE IdUsuarioRol=p_usuario_rol AND Leida=0;
END$$

-- SP: Siguiente correlativo
DROP PROCEDURE IF EXISTS SP_SiguienteCorrelativo$$
CREATE PROCEDURE SP_SiguienteCorrelativo()
BEGIN
    DECLARE v_año VARCHAR(4);
    DECLARE v_num INT;
    SET v_año = YEAR(NOW());
    SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(Codigo,'-',-1) AS UNSIGNED)),0)+1
    INTO v_num FROM Tbl_Registro
    WHERE YEAR(FechaCreacion)=v_año AND Archivado=0;
    SELECT CONCAT('001-', LPAD(v_num,2,'0')) AS correlativo;
END$$

-- SP: Exportar Excel data
DROP PROCEDURE IF EXISTS SP_ExportarRegistros$$
CREATE PROCEDURE SP_ExportarRegistros()
BEGIN
    SELECT r.Codigo, DATE(r.FechaInicio) AS Fecha,
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

-- ═══════════════════════════════════════════════════════════
--  SP: Estadísticas por Cuenta Responsable
-- ═══════════════════════════════════════════════════════════
DELIMITER $

DROP PROCEDURE IF EXISTS SP_EstadisticasCcta$
CREATE PROCEDURE SP_EstadisticasCcta()
BEGIN
    SELECT
        IFNULL(r.CctaResponsable, 'Sin asignar') AS ccta_responsable,
        COUNT(*) AS total,
        SUM(CASE WHEN e.Estado = 'Culminado' THEN 1 ELSE 0 END) AS culminado,
        SUM(CASE WHEN e.Estado = 'Pendiente' THEN 1 ELSE 0 END) AS pendiente,
        SUM(CASE WHEN e.Estado IN ('En Proceso','Enviado','En Revisión') THEN 1 ELSE 0 END) AS proceso
    FROM Tbl_Registro r
    JOIN Tbl_Estado e ON e.idEstado = r.idEstado
    WHERE r.Archivado = 0
    GROUP BY r.CctaResponsable
    ORDER BY total DESC;
END$

DELIMITER ;
