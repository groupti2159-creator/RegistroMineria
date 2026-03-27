-- ============================================================================
-- IMPLEMENTACIÓN DEL SISTEMA DE ROLES PURO
-- ============================================================================
-- Crea la tabla tbl_proyecto_rol_modulo y configura permisos iniciales
-- Basado en el documento TablasAcces
-- ============================================================================

USE desvios_ambientales;

-- ============================================================================
-- PASO 1: Crear tabla tbl_proyecto_rol_modulo
-- ============================================================================
SELECT 'Creando tabla tbl_proyecto_rol_modulo...' AS paso;

CREATE TABLE IF NOT EXISTS tbl_proyecto_rol_modulo (
    idproyectorolmodulo INT AUTO_INCREMENT PRIMARY KEY,
    idproyecto INT NOT NULL COMMENT 'FK a tbl_proyecto',
    idroles INT NOT NULL COMMENT 'FK a tbl_roles',
    idmodulo INT NOT NULL COMMENT 'FK a tbl_modulo',
    fechaasignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Claves foráneas
    FOREIGN KEY (idproyecto) REFERENCES tbl_proyecto(idproyecto) ON DELETE CASCADE,
    FOREIGN KEY (idroles) REFERENCES tbl_roles(idroles) ON DELETE CASCADE,
    FOREIGN KEY (idmodulo) REFERENCES tbl_modulo(idmodulo) ON DELETE CASCADE,
    
    -- Evitar duplicados
    UNIQUE KEY unique_permiso (idproyecto, idroles, idmodulo),
    
    -- Índices para rendimiento
    INDEX idx_proyecto_rol (idproyecto, idroles),
    INDEX idx_rol (idroles)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Permisos por rol: define qué módulos puede ver cada rol en cada proyecto';

SELECT 'Tabla creada exitosamente' AS resultado;

-- ============================================================================
-- PASO 2: Configurar permisos para ADMINISTRADOR (acceso total)
-- ============================================================================
SELECT 'Configurando permisos para Administrador...' AS paso;

-- Administrador (idroles=1) tiene acceso a TODOS los módulos activos
INSERT IGNORE INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
SELECT DISTINCT 
    m.idproyecto,
    1 AS idroles,  -- Administrador
    m.idmodulo
FROM tbl_modulo m
WHERE m.activo = 1
ORDER BY m.idproyecto, m.idmodulo;

SELECT 
    COUNT(*) AS modulos_asignados,
    'Administrador tiene acceso a todos los módulos' AS descripcion
FROM tbl_proyecto_rol_modulo
WHERE idroles = 1;

-- ============================================================================
-- PASO 3: Configurar permisos para SUPERVISOR (solo Mis Reportes)
-- ============================================================================
SELECT 'Configurando permisos para Supervisor...' AS paso;

-- Supervisor (idroles=2) solo tiene acceso a MIS_REPORTES
INSERT IGNORE INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
SELECT 
    m.idproyecto,
    2 AS idroles,  -- Supervisor
    m.idmodulo
FROM tbl_modulo m
WHERE m.codigo = 'MIS_REPORTES'
  AND m.activo = 1;

SELECT 
    COUNT(*) AS modulos_asignados,
    'Supervisor solo tiene acceso a Mis Reportes' AS descripcion
FROM tbl_proyecto_rol_modulo
WHERE idroles = 2;

-- ============================================================================
-- PASO 4: Configurar permisos para TRABAJADOR (solo Mis Reportes)
-- ============================================================================
SELECT 'Configurando permisos para Trabajador...' AS paso;

-- Trabajador (idroles=3) solo tiene acceso a MIS_REPORTES
INSERT IGNORE INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
SELECT 
    m.idproyecto,
    3 AS idroles,  -- Trabajador
    m.idmodulo
FROM tbl_modulo m
WHERE m.codigo = 'MIS_REPORTES'
  AND m.activo = 1;

SELECT 
    COUNT(*) AS modulos_asignados,
    'Trabajador solo tiene acceso a Mis Reportes' AS descripcion
FROM tbl_proyecto_rol_modulo
WHERE idroles = 3;

-- ============================================================================
-- PASO 5: Verificación final
-- ============================================================================
SELECT 'Verificando configuración...' AS paso;

-- Resumen de permisos por rol
SELECT 
    r.idroles,
    r.nombrerol AS rol,
    p.nombre AS proyecto,
    COUNT(prm.idmodulo) AS total_modulos,
    GROUP_CONCAT(m.nombre ORDER BY m.orden SEPARATOR ', ') AS modulos_permitidos
FROM tbl_roles r
LEFT JOIN tbl_proyecto_rol_modulo prm ON prm.idroles = r.idroles
LEFT JOIN tbl_proyecto p ON p.idproyecto = prm.idproyecto
LEFT JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
WHERE r.idroles IN (1, 2, 3)  -- Solo mostrar Admin, Supervisor, Trabajador
GROUP BY r.idroles, r.nombrerol, p.idproyecto, p.nombre
ORDER BY r.idroles, p.nombre;

-- Verificar que todos los roles configurados tienen módulos
SELECT 
    r.idroles,
    r.nombrerol,
    COUNT(prm.idmodulo) AS modulos_asignados,
    CASE 
        WHEN COUNT(prm.idmodulo) = 0 THEN '⚠️ SIN MÓDULOS'
        ELSE '✓ OK'
    END AS estado
FROM tbl_roles r
LEFT JOIN tbl_proyecto_rol_modulo prm ON prm.idroles = r.idroles
WHERE r.idroles IN (1, 2, 3)
GROUP BY r.idroles, r.nombrerol
ORDER BY r.idroles;

-- ============================================================================
-- RESUMEN
-- ============================================================================
SELECT '
╔════════════════════════════════════════════════════════════════╗
║  ✓ SISTEMA DE ROLES IMPLEMENTADO EXITOSAMENTE                 ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  PERMISOS CONFIGURADOS:                                        ║
║  ✓ Administrador → Todos los módulos                          ║
║  ✓ Supervisor → Solo Mis Reportes                             ║
║  ✓ Trabajador → Solo Mis Reportes                             ║
║                                                                ║
║  SIGUIENTE PASO:                                               ║
║  Actualizar routes/auth.py para usar tbl_proyecto_rol_modulo  ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
' AS resumen;

-- ============================================================================
-- NOTAS
-- ============================================================================
/*
DESPUÉS DE EJECUTAR ESTE SCRIPT:

1. La tabla tbl_proyecto_rol_modulo está creada y configurada

2. Permisos por defecto:
   - Administrador (idroles=1): TODOS los módulos
   - Supervisor (idroles=2): Solo MIS_REPORTES
   - Trabajador (idroles=3): Solo MIS_REPORTES

3. Para agregar más permisos a un rol:
   INSERT INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
   VALUES (1, 2, 1);  -- Ejemplo: Supervisor accede a Dashboard

4. Para ver qué módulos tiene un rol:
   SELECT m.nombre 
   FROM tbl_proyecto_rol_modulo prm
   JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
   WHERE prm.idroles = 2 AND prm.idproyecto = 1;

5. Para gestionar permisos desde la interfaz:
   - Ir a /admin/roles
   - Seleccionar proyecto y rol
   - Marcar/desmarcar módulos
*/
