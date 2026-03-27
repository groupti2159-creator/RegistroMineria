-- ============================================================================
-- VERIFICAR MÓDULO CONFIGURACION
-- ============================================================================

-- 1. Ver si existe el módulo CONFIGURACION
SELECT 
    idmodulo,
    codigo,
    nombre,
    idproyecto,
    activo
FROM tbl_modulo
WHERE codigo = 'CONFIGURACION';

-- 2. Ver qué roles tienen acceso a CONFIGURACION
SELECT 
    r.nombrerol AS Rol,
    p.nombre AS Proyecto,
    m.codigo AS Codigo_Modulo,
    m.nombre AS Nombre_Modulo
FROM tbl_proyecto_rol_modulo prm
JOIN tbl_roles r ON r.idroles = prm.idroles
JOIN tbl_proyecto p ON p.idproyecto = prm.idproyecto
JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
WHERE m.codigo = 'CONFIGURACION'
ORDER BY r.idroles;

-- 3. Ver TODOS los módulos del Administrador (rol 1)
SELECT 
    m.codigo AS Codigo,
    m.nombre AS Nombre,
    p.nombre AS Proyecto
FROM tbl_proyecto_rol_modulo prm
JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
JOIN tbl_proyecto p ON p.idproyecto = prm.idproyecto
WHERE prm.idroles = 1  -- Administrador
ORDER BY m.orden;
