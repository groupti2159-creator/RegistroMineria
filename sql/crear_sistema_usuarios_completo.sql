-- ============================================================
-- SISTEMA COMPLETO DE GESTIÓN DE USUARIOS CON PERMISOS
-- ============================================================

USE desvios_ambientales;

-- ============================================================
-- 1. VERIFICAR Y CREAR TABLAS NECESARIAS
-- ============================================================

-- Tabla de Proyectos (si no existe)
CREATE TABLE IF NOT EXISTS tbl_proyecto (
    idproyecto INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(200),
    activo TINYINT(1) DEFAULT 1,
    fechacreacion DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de Módulos con jerarquía (si no existe)
CREATE TABLE IF NOT EXISTS tbl_modulo (
    idmodulo INT AUTO_INCREMENT PRIMARY KEY,
    idproyecto INT NOT NULL,
    idmodulopadre INT NULL,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    icono VARCHAR(50),
    url VARCHAR(200),
    orden INT DEFAULT 0,
    activo TINYINT(1) DEFAULT 1,
    
    FOREIGN KEY (idproyecto) REFERENCES tbl_proyecto(idproyecto) ON DELETE CASCADE,
    FOREIGN KEY (idmodulopadre) REFERENCES tbl_modulo(idmodulo) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de Permisos: Proyecto + Rol → Módulos
CREATE TABLE IF NOT EXISTS tbl_proyecto_rol_modulo (
    idproyectorolmodulo INT AUTO_INCREMENT PRIMARY KEY,
    idproyecto INT NOT NULL,
    idroles INT NOT NULL,
    idmodulo INT NOT NULL,
    
    FOREIGN KEY (idproyecto) REFERENCES tbl_proyecto(idproyecto) ON DELETE CASCADE,
    FOREIGN KEY (idroles) REFERENCES tbl_roles(idroles) ON DELETE CASCADE,
    FOREIGN KEY (idmodulo) REFERENCES tbl_modulo(idmodulo) ON DELETE CASCADE,
    
    UNIQUE KEY unique_project_role_module (idproyecto, idroles, idmodulo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Tabla de Permisos Personalizados por Usuario
CREATE TABLE IF NOT EXISTS tbl_usuario_modulo_personalizado (
    idusuariomodulopersonalizado INT AUTO_INCREMENT PRIMARY KEY,
    idusuariorol INT NOT NULL,
    idmodulo INT NOT NULL,
    permitido TINYINT(1) DEFAULT 1,
    fechaasignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (idusuariorol) REFERENCES tbl_usuariorol(idusuariorol) ON DELETE CASCADE,
    FOREIGN KEY (idmodulo) REFERENCES tbl_modulo(idmodulo) ON DELETE CASCADE,
    
    UNIQUE KEY unique_user_module (idusuariorol, idmodulo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================================
-- 2. STORED PROCEDURES PARA GESTIÓN DE USUARIOS
-- ============================================================

DELIMITER $$

-- SP: Crear Usuario
DROP PROCEDURE IF EXISTS SP_CrearUsuario$$
CREATE PROCEDURE SP_CrearUsuario(
    IN p_dni VARCHAR(20),
    IN p_nombre VARCHAR(100),
    IN p_correo VARCHAR(100),
    IN p_password VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 0 AS success, 'Error al crear usuario' AS message;
    END;
    
    START TRANSACTION;
    
    -- Verificar si el usuario ya existe
    IF EXISTS (SELECT 1 FROM tbl_usuario WHERE idusuario = p_dni) THEN
        SELECT 0 AS success, 'El usuario ya existe' AS message;
        ROLLBACK;
    ELSE
        INSERT INTO tbl_usuario (idusuario, nombrecompleto, correo, contrasena, activo)
        VALUES (p_dni, p_nombre, p_correo, MD5(p_password), 1);
        
        COMMIT;
        SELECT 1 AS success, 'Usuario creado correctamente' AS message;
    END IF;
END$$

-- SP: Crear Asignación Usuario-Proyecto-Rol
DROP PROCEDURE IF EXISTS SP_CrearUsuarioProyectoRol$$
CREATE PROCEDURE SP_CrearUsuarioProyectoRol(
    IN p_usuario VARCHAR(20),
    IN p_proyecto INT,
    IN p_rol INT,
    IN p_area INT,
    IN p_cargo VARCHAR(100)
)
BEGIN
    INSERT INTO tbl_usuariorol (idusuario, idproyecto, idroles, idarea, cargo)
    VALUES (p_usuario, p_proyecto, p_rol, p_area, p_cargo);
    
    SELECT LAST_INSERT_ID() AS idusuariorol;
END$$

-- SP: Guardar Módulo Personalizado
DROP PROCEDURE IF EXISTS SP_GuardarModuloPersonalizado$$
CREATE PROCEDURE SP_GuardarModuloPersonalizado(
    IN p_usuario_rol INT,
    IN p_modulo INT
)
BEGIN
    INSERT INTO tbl_usuario_modulo_personalizado (idusuariorol, idmodulo, permitido)
    VALUES (p_usuario_rol, p_modulo, 1)
    ON DUPLICATE KEY UPDATE permitido = 1;
END$$

-- SP: Listar Usuarios
DROP PROCEDURE IF EXISTS SP_ListarUsuarios$$
CREATE PROCEDURE SP_ListarUsuarios()
BEGIN
    SELECT u.idusuario, u.nombrecompleto, u.correo, u.activo,
           GROUP_CONCAT(DISTINCT r.nombrerol SEPARATOR ', ') AS roles,
           COUNT(DISTINCT ur.idusuariorol) AS cantidadasignaciones
    FROM tbl_usuario u
    LEFT JOIN tbl_usuariorol ur ON ur.idusuario = u.idusuario
    LEFT JOIN tbl_roles r ON r.idroles = ur.idroles
    GROUP BY u.idusuario, u.nombrecompleto, u.correo, u.activo
    ORDER BY u.nombrecompleto;
END$$

-- SP: Obtener Usuario
DROP PROCEDURE IF EXISTS SP_ObtenerUsuario$$
CREATE PROCEDURE SP_ObtenerUsuario(IN p_dni VARCHAR(20))
BEGIN
    SELECT idusuario, nombrecompleto, correo, activo
    FROM tbl_usuario
    WHERE idusuario = p_dni;
END$$

-- SP: Obtener Asignaciones de Usuario
DROP PROCEDURE IF EXISTS SP_ObtenerAsignacionesUsuario$$
CREATE PROCEDURE SP_ObtenerAsignacionesUsuario(IN p_dni VARCHAR(20))
BEGIN
    SELECT ur.idusuariorol,
           p.idproyecto, p.nombre AS nombreproyecto,
           r.idroles, r.nombrerol,
           ur.idarea,
           ar.arearesponsable AS nombrearea,
           ur.cargo
    FROM tbl_usuariorol ur
    JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
    JOIN tbl_roles r ON r.idroles = ur.idroles
    LEFT JOIN tbl_arearesponsable ar ON ar.idarearesponsable = ur.idarea
    WHERE ur.idusuario = p_dni;
END$$

-- SP: Obtener Módulos Personalizados de Usuario
DROP PROCEDURE IF EXISTS SP_ObtenerModulosPersonalizados$$
CREATE PROCEDURE SP_ObtenerModulosPersonalizados(IN p_usuario_rol INT)
BEGIN
    SELECT idmodulo
    FROM tbl_usuario_modulo_personalizado
    WHERE idusuariorol = p_usuario_rol AND permitido = 1;
END$$

-- SP: Obtener Módulos Personalizados Completos (para login)
DROP PROCEDURE IF EXISTS SP_ObtenerModulosPersonalizadosCompletos$$
CREATE PROCEDURE SP_ObtenerModulosPersonalizadosCompletos(IN p_usuario_rol INT)
BEGIN
    SELECT m.idmodulo, m.idmodulopadre, m.codigo, m.nombre, m.icono, m.url, m.orden
    FROM tbl_modulo m
    JOIN tbl_usuario_modulo_personalizado ump ON ump.idmodulo = m.idmodulo
    WHERE ump.idusuariorol = p_usuario_rol 
      AND ump.permitido = 1
      AND m.activo = 1
    ORDER BY m.orden;
END$$

-- SP: Listar Proyectos
DROP PROCEDURE IF EXISTS SP_ListarProyectos$$
CREATE PROCEDURE SP_ListarProyectos()
BEGIN
    SELECT idproyecto, codigo, nombre, descripcion, activo
    FROM tbl_proyecto
    WHERE activo = 1
    ORDER BY nombre;
END$$

-- SP: Listar Roles
DROP PROCEDURE IF EXISTS SP_ListarRoles$$
CREATE PROCEDURE SP_ListarRoles()
BEGIN
    SELECT idroles, nombrerol, descripcion
    FROM tbl_roles
    ORDER BY nombrerol;
END$$

-- SP: Listar Áreas
DROP PROCEDURE IF EXISTS SP_ListarAreas$$
CREATE PROCEDURE SP_ListarAreas()
BEGIN
    SELECT idarearesponsable, arearesponsable
    FROM tbl_arearesponsable
    ORDER BY arearesponsable;
END$$

-- SP: Listar Módulos de Proyecto
DROP PROCEDURE IF EXISTS SP_ListarModulosProyecto$$
CREATE PROCEDURE SP_ListarModulosProyecto(IN p_proyecto_id INT)
BEGIN
    SELECT idmodulo, idmodulopadre, codigo, nombre, icono, url, orden
    FROM tbl_modulo
    WHERE idproyecto = p_proyecto_id AND activo = 1
    ORDER BY orden;
END$$

DELIMITER ;

-- ============================================================
-- 3. DATOS INICIALES (si no existen)
-- ============================================================

-- Insertar proyecto por defecto si no existe
INSERT IGNORE INTO tbl_proyecto (idproyecto, codigo, nombre, descripcion) 
VALUES (1, 'AMBIENTE', 'Proyecto Ambiente', 'Sistema de gestión ambiental');

-- Verificar que existan módulos básicos
SELECT 'Sistema de gestión de usuarios configurado correctamente' AS Mensaje;

-- ============================================================
-- 4. VERIFICACIÓN
-- ============================================================

SELECT 'Verificando tablas...' AS Paso;

SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'desvios_ambientales' AND table_name = 'tbl_proyecto') > 0
        THEN '✅ tbl_proyecto existe'
        ELSE '❌ tbl_proyecto NO existe'
    END AS tbl_proyecto,
    CASE 
        WHEN (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'desvios_ambientales' AND table_name = 'tbl_modulo') > 0
        THEN '✅ tbl_modulo existe'
        ELSE '❌ tbl_modulo NO existe'
    END AS tbl_modulo,
    CASE 
        WHEN (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'desvios_ambientales' AND table_name = 'tbl_proyecto_rol_modulo') > 0
        THEN '✅ tbl_proyecto_rol_modulo existe'
        ELSE '❌ tbl_proyecto_rol_modulo NO existe'
    END AS tbl_proyecto_rol_modulo,
    CASE 
        WHEN (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'desvios_ambientales' AND table_name = 'tbl_usuario_modulo_personalizado') > 0
        THEN '✅ tbl_usuario_modulo_personalizado existe'
        ELSE '❌ tbl_usuario_modulo_personalizado NO existe'
    END AS tbl_usuario_modulo_personalizado;

SELECT 'Verificando stored procedures...' AS Paso;

SELECT COUNT(*) AS total_procedures
FROM information_schema.ROUTINES 
WHERE ROUTINE_SCHEMA = 'desvios_ambientales' 
  AND ROUTINE_TYPE = 'PROCEDURE' 
  AND ROUTINE_NAME LIKE 'SP_%';

SELECT '¡Sistema listo para usar!' AS Estado;
