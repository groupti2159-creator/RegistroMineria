-- ============================================================
--  DESVÃOS AMBIENTALES â€” MySQL Schema COMPLETO
--  Con Stored Procedures y tabla de historial
-- ============================================================

CREATE DATABASE IF NOT EXISTS desvios_ambientales
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE desvios_ambientales;

-- â”€â”€â”€ TABLAS MAESTRAS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

CREATE TABLE IF NOT EXISTS Tbl_Roles (
    idRoles     INT AUTO_INCREMENT PRIMARY KEY,
    NombreRol   VARCHAR(50) NOT NULL,
    Descripcion VARCHAR(200)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_Estado (
    idEstado    INT AUTO_INCREMENT PRIMARY KEY,
    Estado      VARCHAR(50) NOT NULL,
    Descripcion VARCHAR(200),
    Orden       INT DEFAULT 0
    Orden       INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_Riesgo (
    IdRiesgo INT AUTO_INCREMENT PRIMARY KEY,
    Riesgo   VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_DescripcionTipo (
    IdDescripcionTipo INT AUTO_INCREMENT PRIMARY KEY,
    DescripcionTipo   VARCHAR(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_AreaReportante (
    idAreaReportante INT AUTO_INCREMENT PRIMARY KEY,
    AreaReportante   VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_AreaResponsable (
    idAreaResponsable INT AUTO_INCREMENT PRIMARY KEY,
    AreaResponsable   VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_Ubicacion (
    idUbicacion INT AUTO_INCREMENT PRIMARY KEY,
    Ubicacion   VARCHAR(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_EstadoImagen (
    idEstadoImagen INT AUTO_INCREMENT PRIMARY KEY,
    EstadoImagen   VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_TipoImagen (
    idTipoImagen INT AUTO_INCREMENT PRIMARY KEY,
    TipoImagen   VARCHAR(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- â”€â”€â”€ USUARIOS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

CREATE TABLE IF NOT EXISTS Tbl_Usuario (
    idUsuario      VARCHAR(20) PRIMARY KEY,
    NombreCompleto VARCHAR(100) NOT NULL,
    Correo         VARCHAR(100),
    Contrasena     VARCHAR(255) NOT NULL,
    Activo         TINYINT(1) DEFAULT 1,
    FechaCreacion  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS Tbl_UsuarioRol (
    IdUsuarioRol    INT AUTO_INCREMENT PRIMARY KEY,
    idUsuario       VARCHAR(20) NOT NULL,
    idRoles         INT NOT NULL,
    FechaAsignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idUsuario) REFERENCES Tbl_Usuario(idUsuario) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (idRoles)   REFERENCES Tbl_Roles(idRoles)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- â”€â”€â”€ REGISTRO PRINCIPAL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

CREATE TABLE IF NOT EXISTS Tbl_Registro (
    IdRegistro          INT AUTO_INCREMENT PRIMARY KEY,
    Codigo              VARCHAR(20),
    FechaInicio         DATETIME NOT NULL,
    FechaEjecucion      DATETIME,
    Descripcion         VARCHAR(500) NOT NULL,
    Accion              VARCHAR(300),
    NotasLevantamiento  TEXT,
    idAreaReportante    INT NOT NULL,
    idAreaResponsable   INT NOT NULL,
    idUbicacion         INT NOT NULL,
    IdRiesgo            INT NOT NULL,
    IdDescripcionTipo   INT NOT NULL,
    idEstado            INT NOT NULL,
    IdUsuarioRolCreador INT NOT NULL,
    PersonalResponsable VARCHAR(100),
    CctaResponsable     INT NULL,
    Archivado           TINYINT(1) DEFAULT 0,
    FechaArchivado      DATETIME NULL,
    IdUsuarioRolArchivador INT NULL,
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


-- â”€â”€â”€ IMÃGENES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

CREATE TABLE IF NOT EXISTS Tbl_ImagenRegistro (
    IdImagen            INT AUTO_INCREMENT PRIMARY KEY,
    IdRegistro          INT NOT NULL,
    IdUsuarioRol        INT NOT NULL,
    idTipoImagen        INT NOT NULL,
    idEstadoImagen      INT NOT NULL,
    RutaImagen          VARCHAR(300) NOT NULL,
    NombreArchivo       VARCHAR(100),
    TamanoKB            INT,
    MotivoRechazo       VARCHAR(300),
    IdUsuarioRolRevisor INT,
    FechaRevision       DATETIME,
    FechaSubida         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdRegistro)     REFERENCES Tbl_Registro(IdRegistro) ON DELETE CASCADE,
    FOREIGN KEY (IdUsuarioRol)   REFERENCES Tbl_UsuarioRol(IdUsuarioRol),
    FOREIGN KEY (idTipoImagen)   REFERENCES Tbl_TipoImagen(idTipoImagen),
    FOREIGN KEY (idEstadoImagen) REFERENCES Tbl_EstadoImagen(idEstadoImagen)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- â”€â”€â”€ HISTORIAL APROBACIÃ“N â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

CREATE TABLE IF NOT EXISTS Tbl_HistorialAprobacion (
    IdHistorial           INT AUTO_INCREMENT PRIMARY KEY,
    IdImagen              INT NOT NULL,
    IdRegistro            INT NOT NULL,
    IdUsuarioRolRevisor   INT NOT NULL,
    DecisionTomada        VARCHAR(20) NOT NULL,
    Comentarios           VARCHAR(300),
    FechaDecision         DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdImagen)            REFERENCES Tbl_ImagenRegistro(IdImagen),
    FOREIGN KEY (IdRegistro)          REFERENCES Tbl_Registro(IdRegistro),
    FOREIGN KEY (IdUsuarioRolRevisor) REFERENCES Tbl_UsuarioRol(IdUsuarioRol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- â”€â”€â”€ NOTIFICACIONES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

CREATE TABLE IF NOT EXISTS Tbl_Notificacion (
    IdNotificacion INT AUTO_INCREMENT PRIMARY KEY,
    IdUsuarioRol   INT NOT NULL,
    Mensaje        VARCHAR(300) NOT NULL,
    Leida          TINYINT(1) DEFAULT 0,
    Tipo           VARCHAR(20) DEFAULT 'info',
    IdRegistro     INT,
    FechaCreacion  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IdUsuarioRol) REFERENCES Tbl_UsuarioRol(IdUsuarioRol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- â”€â”€â”€ DATOS INICIALES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

INSERT IGNORE INTO Tbl_Roles (nombrerol, descripcion) VALUES
('Administrador', 'Crea y aprueba registros'),
('Supervisor', 'Supervisa y valida'),
('Trabajador', 'Resuelve registros asignados');

INSERT IGNORE INTO Tbl_Estado (estado, descripcion, orden) VALUES
('Pendiente',   'Registro creado, esperando imágenes', 1),
('Asignado',    'Asignado al personal', 2),
('En Proceso',  'Imágenes subidas, esperando validación', 3),
('Enviado',     'Trabajador subió imagen', 4),
('En Revisión', 'Supervisor validó', 5),
('Culminado',   'Imágenes validadas y aprobadas', 6),
('Rechazado',   'Rechazado, reintentar', 7),
('Cerrado',     'Cerrado', 8);

INSERT IGNORE INTO Tbl_Riesgo (riesgo) VALUES
('Bajo'),('Medio'),('Alto'),('Crítico');

INSERT IGNORE INTO Tbl_DescripcionTipo (descripciontipo) VALUES
('Incumplimiento de IGA'),
('Riesgo Eléctrico'),
('Riesgo Civil'),
('Riesgo Mecánico'),
('Seguridad Industrial'),
('Ambiental'),
('Polvo'),
('Disposición Residuos Peligrosos'),
('Disposición Desmonte - Escombros'),
('Lixiviados'),
('Lodo'),
('RAEES - Residuos Electrónicos'),
('NFU - Neumáticos Fuera de Uso');

INSERT IGNORE INTO Tbl_AreaReportante (areareportante) VALUES
('Los Andes'),('Operaciones'),
('Mantenimiento'),('Seguridad'),
('Geología'),('Medio Ambiente');

INSERT IGNORE INTO Tbl_AreaResponsable (arearesponsable) VALUES
('Proyectos'),('Mantenimiento General'),
('Ingeniería'),('Seguridad Industrial'),
('Geología'),('Medio Ambiente');

INSERT IGNORE INTO Tbl_Ubicacion (ubicacion) VALUES
('Zona I - NORTE - Sector A'),
('Zona II - Mascota - Bodega Pique Central'),
('Zona III - Sur - Sector B'),
('Patio Exterior'),
('Almacén Central'),
('Zona I - OESTE - Planta de Procesamiento');

INSERT IGNORE INTO Tbl_EstadoImagen (estadoimagen) VALUES ('Pendiente'),('Aprobada'),('Rechazada');

INSERT IGNORE INTO Tbl_TipoImagen (idtipoimagen, tipoimagen) VALUES
(1,'ImagenError'),
(2,'ImagenLevantamiento'),
(3,'ImagenValidacion');

INSERT IGNORE INTO Tbl_Usuario VALUES
('12345678','Eco Supervisor','admin@eco.com',   MD5('admin123'),1,NOW()),
('87654321','Juan Supervisor','sup@eco.com',    MD5('sup123'),  1,NOW()),
('11223344','Carlos Trabajador','trab@eco.com', MD5('trab123'), 1,NOW());

INSERT IGNORE INTO Tbl_UsuarioRol (idusuario, idroles) VALUES
('12345678', 1),
('87654321', 2),
('11223344', 3);

-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

-- ═══════════════════════════════════════════════════════════
--  STORED PROCEDURES
-- ═══════════════════════════════════════════════════════════

DELIMITER $

-- SP: Login
DROP PROCEDURE IF EXISTS SP_Login$
CREATE PROCEDURE SP_Login(IN p_dni VARCHAR(20), IN p_pass VARCHAR(255))
BEGIN
    SELECT u.idUsuario, u.NombreCompleto, u.Correo, u.Activo,
           ur.IdUsuarioRol, r.idRoles, r.NombreRol
    FROM tbl_usuario u
    JOIN tbl_usuariorol ur ON ur.idUsuario = u.idUsuario
    JOIN tbl_roles r ON r.idRoles = ur.idRoles
    WHERE u.idUsuario = p_dni AND u.Contrasena = MD5(p_pass) AND u.Activo = 1
    LIMIT 1;
END$

-- SP: Dashboard stats
DROP PROCEDURE IF EXISTS SP_DashboardStats$
CREATE PROCEDURE SP_DashboardStats()
BEGIN
    SELECT
        COUNT(*) AS total,
        SUM(CASE WHEN e.Estado = 'Culminado' THEN 1 ELSE 0 END) AS culminados,
        SUM(CASE WHEN e.Estado IN ('En Proceso','Enviado','En Revisión') THEN 1 ELSE 0 END) AS en_proceso,
        SUM(CASE WHEN e.Estado = 'Pendiente' THEN 1 ELSE 0 END) AS pendientes
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    WHERE r.Archivado = 0;
END$

-- SP: Listar registros admin
DROP PROCEDURE IF EXISTS SP_ListarRegistros$
CREATE PROCEDURE SP_ListarRegistros(IN p_estado VARCHAR(50))
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
      AND (p_estado IS NULL OR p_estado = '' OR e.Estado = p_estado)
    ORDER BY r.FechaCreacion DESC;
END$

-- SP: Listar registros supervisor
DROP PROCEDURE IF EXISTS SP_ListarRegistrosSupervisor$
CREATE PROCEDURE SP_ListarRegistrosSupervisor(IN p_estado VARCHAR(50))
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
      AND (p_estado IS NULL OR p_estado = '' OR e.Estado = p_estado)
    ORDER BY r.FechaCreacion DESC;
END$

-- SP: Detalle registro
DROP PROCEDURE IF EXISTS SP_DetalleRegistro$
CREATE PROCEDURE SP_DetalleRegistro(IN p_id INT)
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.Accion, r.NotasLevantamiento, r.PersonalResponsable, r.DniResponsable,
           r.CctaResponsable,
           ccta.AreaReportante AS NombreCctaResponsable,
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
    JOIN tbl_usuariorol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    LEFT JOIN tbl_areareportante ccta ON ccta.idAreaReportante = r.CctaResponsable
    WHERE r.IdRegistro = p_id;
END$

-- SP: Imágenes de registro
DROP PROCEDURE IF EXISTS SP_ImagenesRegistro$
CREATE PROCEDURE SP_ImagenesRegistro(IN p_id INT)
BEGIN
    SELECT i.IdImagen, i.RutaImagen, i.NombreArchivo, i.TamanoKB,
           i.MotivoRechazo, i.FechaSubida, i.FechaRevision,
           ti.TipoImagen, ti.idTipoImagen,
           ei.EstadoImagen, ei.idEstadoImagen,
           u.NombreCompleto AS Subidor
    FROM tbl_imagenregistro i
    JOIN tbl_tipoimagen ti ON ti.idTipoImagen = i.idTipoImagen
    JOIN tbl_estadoimagen ei ON ei.idEstadoImagen = i.idEstadoImagen
    JOIN tbl_usuariorol ur ON ur.IdUsuarioRol = i.IdUsuarioRol
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    WHERE i.IdRegistro = p_id AND i.idEstadoImagen != 3
    ORDER BY i.FechaSubida;
END$

-- SP: Crear registro (AUTO_INCREMENT, retorna idregistro)
DROP PROCEDURE IF EXISTS SP_CrearRegistro$
CREATE PROCEDURE SP_CrearRegistro(
    IN p_codigo VARCHAR(20),
    IN p_fecha DATETIME, IN p_fecha_ejec DATETIME,
    IN p_desc VARCHAR(500), IN p_accion VARCHAR(300),
    IN p_area_rep INT, IN p_area_res INT,
    IN p_ubic INT, IN p_riesgo INT,
    IN p_tipo INT, IN p_estado INT,
    IN p_creador INT, IN p_personal VARCHAR(100),
    IN p_ccta INT, IN p_dni VARCHAR(20)
)
BEGIN
    INSERT INTO tbl_registro (
        Codigo, FechaInicio, FechaEjecucion, Descripcion, Accion,
        idAreaReportante, idAreaResponsable, idUbicacion, IdRiesgo,
        IdDescripcionTipo, idEstado, IdUsuarioRolCreador,
        PersonalResponsable, DniResponsable, CctaResponsable
    ) VALUES (
        p_codigo, p_fecha, p_fecha_ejec, p_desc, p_accion,
        p_area_rep, p_area_res, p_ubic, p_riesgo,
        p_tipo, p_estado, p_creador, p_personal,
        NULLIF(p_dni, ''), NULLIF(p_ccta, 0)
    );
    SELECT LAST_INSERT_ID() AS idregistro;
END$

-- SP: Actualizar registro
DROP PROCEDURE IF EXISTS SP_ActualizarRegistro$
CREATE PROCEDURE SP_ActualizarRegistro(
    IN p_id INT, IN p_fecha DATETIME, IN p_fecha_ejec DATETIME,
    IN p_desc VARCHAR(500), IN p_accion VARCHAR(300),
    IN p_area_rep INT, IN p_area_res INT,
    IN p_ubic INT, IN p_riesgo INT,
    IN p_tipo INT, IN p_estado INT,
    IN p_personal VARCHAR(100), IN p_ccta INT,
    IN p_dni VARCHAR(20)
)
BEGIN
    UPDATE tbl_registro SET
        FechaInicio=p_fecha, FechaEjecucion=p_fecha_ejec,
        Descripcion=p_desc, Accion=p_accion,
        idAreaReportante=p_area_rep, idAreaResponsable=p_area_res,
        idUbicacion=p_ubic, IdRiesgo=p_riesgo,
        IdDescripcionTipo=p_tipo, idEstado=p_estado,
        PersonalResponsable=p_personal,
        DniResponsable=NULLIF(p_dni, ''),
        CctaResponsable=NULLIF(p_ccta, 0)
    WHERE IdRegistro=p_id;
    SELECT ROW_COUNT() AS affected;
END$

-- SP: Archivar registro
DROP PROCEDURE IF EXISTS SP_ArchivarRegistro$
CREATE PROCEDURE SP_ArchivarRegistro(IN p_id INT, IN p_archivador INT)
BEGIN
    UPDATE tbl_registro
    SET Archivado=1, FechaArchivado=NOW(), IdUsuarioRolArchivador=p_archivador
    WHERE IdRegistro=p_id AND idEstado=6;
    SELECT ROW_COUNT() AS affected;
END$

-- SP: Historial admin
DROP PROCEDURE IF EXISTS SP_HistorialAdmin$
CREATE PROCEDURE SP_HistorialAdmin()
BEGIN
    SELECT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.PersonalResponsable, r.FechaArchivado,
           e.Estado, ar.AreaReportante, ub.Ubicacion, ri.Riesgo,
           u.NombreCompleto AS Creador, ua.NombreCompleto AS Archivador
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_usuariorol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    LEFT JOIN tbl_usuariorol ura ON ura.IdUsuarioRol = r.IdUsuarioRolArchivador
    LEFT JOIN tbl_usuario ua ON ua.idUsuario = ura.idUsuario
    WHERE r.Archivado = 1
    ORDER BY r.FechaArchivado DESC;
END$

-- SP: Historial supervisor
DROP PROCEDURE IF EXISTS SP_HistorialSupervisor$
CREATE PROCEDURE SP_HistorialSupervisor(IN p_usuario_rol INT)
BEGIN
    SELECT DISTINCT r.IdRegistro, r.Codigo, r.FechaInicio, r.FechaEjecucion,
           r.Descripcion, r.PersonalResponsable, r.FechaArchivado,
           e.Estado, ar.AreaReportante, ub.Ubicacion, ri.Riesgo,
           u.NombreCompleto AS Creador
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado = r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
    JOIN tbl_ubicacion ub ON ub.idUbicacion = r.idUbicacion
    JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
    JOIN tbl_usuariorol ur ON ur.IdUsuarioRol = r.IdUsuarioRolCreador
    JOIN tbl_usuario u ON u.idUsuario = ur.idUsuario
    LEFT JOIN tbl_imagenregistro img ON img.IdRegistro = r.IdRegistro AND img.IdUsuarioRol = p_usuario_rol
    WHERE r.Archivado = 1 AND img.IdRegistro IS NOT NULL
    ORDER BY r.FechaArchivado DESC;
END$

-- SP: Guardar imagen (AUTO_INCREMENT)
DROP PROCEDURE IF EXISTS SP_GuardarImagen$
CREATE PROCEDURE SP_GuardarImagen(
    IN p_registro INT, IN p_usuario_rol INT,
    IN p_tipo INT, IN p_estado INT,
    IN p_ruta VARCHAR(300), IN p_nombre VARCHAR(100), IN p_tamano INT
)
BEGIN
    DECLARE cnt INT;
    SELECT COUNT(*) INTO cnt FROM tbl_imagenregistro
    WHERE IdRegistro=p_registro AND idTipoImagen=p_tipo AND idEstadoImagen != 3;
    IF cnt < 5 THEN
        INSERT INTO tbl_imagenregistro
            (IdRegistro,IdUsuarioRol,idTipoImagen,idEstadoImagen,RutaImagen,NombreArchivo,TamanoKB)
        VALUES (p_registro,p_usuario_rol,p_tipo,p_estado,p_ruta,p_nombre,p_tamano);

        -- Solo cambiar a "En Proceso" (3) cuando el supervisor sube levantamientos (tipo 2)
        IF p_tipo = 2 THEN
            UPDATE tbl_registro
            SET idEstado = 3
            WHERE IdRegistro = p_registro AND idEstado IN (1, 2);
        END IF;

        SELECT LAST_INSERT_ID() AS idimagen, 1 AS ok, 'Imagen guardada' AS msg;
    ELSE
        SELECT 0 AS idimagen, 0 AS ok, 'Máximo 5 imágenes por tipo' AS msg;
    END IF;
END$

-- SP: Cambiar estado
DROP PROCEDURE IF EXISTS SP_CambiarEstado$
CREATE PROCEDURE SP_CambiarEstado(IN p_id INT, IN p_estado INT)
BEGIN
    UPDATE tbl_registro SET idEstado=p_estado WHERE IdRegistro=p_id;
    SELECT ROW_COUNT() AS affected;
END$

-- SP: Validar imagen
DROP PROCEDURE IF EXISTS SP_ValidarImagen$
CREATE PROCEDURE SP_ValidarImagen(
    IN p_imagen INT, IN p_registro INT,
    IN p_revisor INT, IN p_decision VARCHAR(20),
    IN p_comentario VARCHAR(300)
)
BEGIN
    DECLARE v_estado INT;
    IF p_decision = 'APROBADA' THEN SET v_estado = 2;
    ELSE SET v_estado = 3; END IF;

    UPDATE tbl_imagenregistro
    SET idEstadoImagen=v_estado, IdUsuarioRolRevisor=p_revisor,
        FechaRevision=NOW(), MotivoRechazo=IF(p_decision='RECHAZADA',p_comentario,NULL)
    WHERE IdImagen=p_imagen;

    INSERT INTO tbl_historialaprobacion
        (IdImagen,IdRegistro,IdUsuarioRolRevisor,DecisionTomada,Comentarios)
    VALUES (p_imagen,p_registro,p_revisor,p_decision,p_comentario);

    IF p_decision = 'APROBADA' THEN
        IF EXISTS (
            SELECT 1 FROM tbl_imagenregistro
            WHERE IdRegistro=p_registro AND idTipoImagen=2 AND idEstadoImagen=2
        ) AND NOT EXISTS (
            SELECT 1 FROM tbl_imagenregistro
            WHERE IdRegistro=p_registro AND idTipoImagen=2 AND idEstadoImagen=1
        ) THEN
            UPDATE tbl_registro SET idEstado=6 WHERE IdRegistro=p_registro;
        END IF;
    ELSE
        UPDATE tbl_registro SET idEstado=1 WHERE IdRegistro=p_registro;
    END IF;
    SELECT ROW_COUNT() AS affected;
END$

-- SP: Eliminar imagen
DROP PROCEDURE IF EXISTS SP_EliminarImagen$
CREATE PROCEDURE SP_EliminarImagen(IN p_id INT)
BEGIN
    DELETE FROM tbl_imagenregistro WHERE IdImagen=p_id;
    SELECT ROW_COUNT() AS affected;
END$

-- SP: Crear notificación (AUTO_INCREMENT)
DROP PROCEDURE IF EXISTS SP_CrearNotificacion$
CREATE PROCEDURE SP_CrearNotificacion(
    IN p_usuario_rol INT, IN p_mensaje VARCHAR(300),
    IN p_tipo VARCHAR(20), IN p_registro INT
)
BEGIN
    INSERT INTO tbl_notificacion(IdUsuarioRol,Mensaje,Tipo,IdRegistro)
    VALUES(p_usuario_rol,p_mensaje,p_tipo,p_registro);
END$

-- SP: Notificaciones del usuario
DROP PROCEDURE IF EXISTS SP_Notificaciones$
CREATE PROCEDURE SP_Notificaciones(IN p_usuario_rol INT)
BEGIN
    SELECT IdNotificacion, Mensaje, Leida, Tipo, IdRegistro, FechaCreacion
    FROM tbl_notificacion
    WHERE IdUsuarioRol=p_usuario_rol
    ORDER BY FechaCreacion DESC LIMIT 20;
END$

-- SP: Marcar notificacion leida
DROP PROCEDURE IF EXISTS SP_LeerNotificacion$
CREATE PROCEDURE SP_LeerNotificacion(IN p_id INT)
BEGIN
    UPDATE tbl_notificacion SET Leida=1 WHERE IdNotificacion=p_id;
END$

-- SP: Contar notificaciones no leídas
DROP PROCEDURE IF EXISTS SP_ContarNotificaciones$
CREATE PROCEDURE SP_ContarNotificaciones(IN p_usuario_rol INT)
BEGIN
    SELECT COUNT(*) AS total FROM tbl_notificacion
    WHERE IdUsuarioRol=p_usuario_rol AND Leida=0;
END$

-- SP: Siguiente correlativo
DROP PROCEDURE IF EXISTS SP_SiguienteCorrelativo$
CREATE PROCEDURE SP_SiguienteCorrelativo()
BEGIN
    DECLARE v_año VARCHAR(4);
    DECLARE v_num INT;
    SET v_año = YEAR(NOW());
    SELECT IFNULL(MAX(CAST(SUBSTRING_INDEX(Codigo,'-',-1) AS UNSIGNED)),0)+1
    INTO v_num FROM tbl_registro
    WHERE YEAR(FechaCreacion)=v_año AND Archivado=0;
    SELECT CONCAT('001-', LPAD(v_num,2,'0')) AS correlativo;
END$

-- SP: Exportar Excel
DROP PROCEDURE IF EXISTS SP_ExportarRegistros$
CREATE PROCEDURE SP_ExportarRegistros()
BEGIN
    SELECT r.IdRegistro,
           r.Codigo, DATE(r.FechaInicio) AS Fecha,
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
END$

-- SP: Estadísticas por área
DROP PROCEDURE IF EXISTS SP_EstadisticasAreas$
CREATE PROCEDURE SP_EstadisticasAreas(IN p_fecha_ini DATE, IN p_fecha_fin DATE)
BEGIN
    SELECT ar.AreaReportante,
        COUNT(*) AS total,
        SUM(CASE WHEN e.Estado='Culminado' THEN 1 ELSE 0 END) AS culminado,
        SUM(CASE WHEN e.Estado='Pendiente' THEN 1 ELSE 0 END) AS pendiente,
        SUM(CASE WHEN e.Estado IN ('En Proceso','Enviado','En Revisión') THEN 1 ELSE 0 END) AS proceso
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado=r.idEstado
    JOIN tbl_areareportante ar ON ar.idAreaReportante=r.idAreaReportante
    WHERE r.Archivado=0
      AND (p_fecha_ini IS NULL OR DATE(r.FechaCreacion) >= p_fecha_ini)
      AND (p_fecha_fin IS NULL OR DATE(r.FechaCreacion) <= p_fecha_fin)
    GROUP BY ar.idAreaReportante, ar.AreaReportante
    ORDER BY total DESC;
END$

-- SP: Estadísticas por cuenta responsable
DROP PROCEDURE IF EXISTS SP_EstadisticasCcta$
CREATE PROCEDURE SP_EstadisticasCcta(IN p_fecha_ini DATE, IN p_fecha_fin DATE)
BEGIN
    SELECT IFNULL(r.CctaResponsable,'Sin asignar') AS ccta_responsable,
        COUNT(*) AS total,
        SUM(CASE WHEN e.Estado='Culminado' THEN 1 ELSE 0 END) AS culminado,
        SUM(CASE WHEN e.Estado='Pendiente' THEN 1 ELSE 0 END) AS pendiente,
        SUM(CASE WHEN e.Estado IN ('En Proceso','Enviado','En Revisión') THEN 1 ELSE 0 END) AS proceso
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado=r.idEstado
    WHERE r.Archivado=0
      AND (p_fecha_ini IS NULL OR DATE(r.FechaCreacion) >= p_fecha_ini)
      AND (p_fecha_fin IS NULL OR DATE(r.FechaCreacion) <= p_fecha_fin)
    GROUP BY r.CctaResponsable
    ORDER BY total DESC;
END$

-- SP: Estadísticas por tipo
DROP PROCEDURE IF EXISTS SP_Estadisticas_Tipos_Pendientes$
CREATE PROCEDURE SP_Estadisticas_Tipos_Pendientes(IN p_fecha_ini DATE, IN p_fecha_fin DATE)
BEGIN
    SELECT dt.DescripcionTipo,
        COUNT(*) AS total,
        SUM(CASE WHEN e.Estado='Culminado' THEN 1 ELSE 0 END) AS culminado,
        SUM(CASE WHEN e.Estado='Pendiente' THEN 1 ELSE 0 END) AS pendiente,
        SUM(CASE WHEN e.Estado IN ('En Proceso','Enviado','En Revisión') THEN 1 ELSE 0 END) AS proceso
    FROM tbl_registro r
    JOIN tbl_estado e ON e.idEstado=r.idEstado
    JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo=r.IdDescripcionTipo
    WHERE r.Archivado=0
      AND (p_fecha_ini IS NULL OR DATE(r.FechaCreacion) >= p_fecha_ini)
      AND (p_fecha_fin IS NULL OR DATE(r.FechaCreacion) <= p_fecha_fin)
    GROUP BY dt.IdDescripcionTipo, dt.DescripcionTipo
    ORDER BY total DESC;
END$

DELIMITER ;

