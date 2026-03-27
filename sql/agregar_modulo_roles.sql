-- ============================================================================
-- AGREGAR MÓDULO "ROLES" DENTRO DE CONFIGURACIÓN
-- ============================================================================

-- 1. Obtener el ID del módulo padre CONFIGURACION
SET @id_config = (SELECT idmodulo FROM tbl_modulo WHERE codigo = 'CONFIGURACION' LIMIT 1);
SET @id_proyecto = (SELECT idproyecto FROM tbl_modulo WHERE codigo = 'CONFIGURACION' LIMIT 1);

-- 2. Verificar si ya existe el módulo ROLES
SELECT 
    CASE 
        WHEN EXISTS(SELECT 1 FROM tbl_modulo WHERE codigo = 'ROLES') 
        THEN 'El módulo ROLES ya existe'
        ELSE 'Creando módulo ROLES...'
    END AS estado;

-- 3. Insertar módulo ROLES si no existe
INSERT INTO tbl_modulo (idproyecto, idmodulopadre, codigo, nombre, icono, url, orden, activo)
SELECT 
    @id_proyecto,
    @id_config,
    'ROLES',
    'Gestión de Roles',
    'shield',
    '/admin/roles',
    2,  -- Orden 2 (después de Usuarios que probablemente sea 1)
    1
WHERE NOT EXISTS (SELECT 1 FROM tbl_modulo WHERE codigo = 'ROLES');

-- 4. Asignar el módulo ROLES al Administrador
SET @id_roles = (SELECT idmodulo FROM tbl_modulo WHERE codigo = 'ROLES' LIMIT 1);

INSERT INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
SELECT 
    @id_proyecto,
    1,  -- Administrador
    @id_roles
WHERE NOT EXISTS (
    SELECT 1 FROM tbl_proyecto_rol_modulo 
    WHERE idproyecto = @id_proyecto 
      AND idroles = 1 
      AND idmodulo = @id_roles
);

-- 5. Verificar resultado
SELECT 
    m.codigo AS Codigo,
    m.nombre AS Nombre,
    m.url AS URL,
    m.orden AS Orden,
    CASE WHEN m.idmodulopadre IS NULL THEN 'PADRE' ELSE 'HIJO' END AS Tipo,
    p.nombre AS Proyecto
FROM tbl_modulo m
LEFT JOIN tbl_proyecto p ON p.idproyecto = m.idproyecto
WHERE m.codigo IN ('CONFIGURACION', 'ROLES')
   OR m.idmodulopadre = @id_config
ORDER BY m.idmodulopadre, m.orden;

-- 6. Verificar que Administrador tiene acceso
SELECT 
    r.nombrerol AS Rol,
    m.codigo AS Codigo_Modulo,
    m.nombre AS Nombre_Modulo
FROM tbl_proyecto_rol_modulo prm
JOIN tbl_roles r ON r.idroles = prm.idroles
JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
WHERE m.codigo = 'ROLES'
ORDER BY r.idroles;
