-- ============================================================
-- MIGRACIÓN: Sistema Antiguo → Sistema Nuevo de Permisos
-- ============================================================
-- Migra permisos de tbl_modulo_permiso a tbl_proyecto_rol_modulo
-- ============================================================

USE desvios_ambientales;

-- ============================================================
-- 1. ANÁLISIS PREVIO
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '1. ANÁLISIS DEL SISTEMA ACTUAL' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- Contar permisos en sistema antiguo
SELECT 
    'Sistema Antiguo (tbl_modulo_permiso)' as sistema,
    COUNT(*) as total_permisos,
    COUNT(DISTINCT idroles) as roles_distintos,
    COUNT(DISTINCT idmodulo) as modulos_distintos
FROM tbl_modulo_permiso;

-- Contar permisos en sistema nuevo
SELECT 
    'Sistema Nuevo (tbl_proyecto_rol_modulo)' as sistema,
    COUNT(*) as total_permisos,
    COUNT(DISTINCT idroles) as roles_distintos,
    COUNT(DISTINCT idmodulo) as modulos_distintos,
    COUNT(DISTINCT idproyecto) as proyectos_distintos
FROM tbl_proyecto_rol_modulo;

-- ============================================================
-- 2. VISTA PREVIA DE LA MIGRACIÓN
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '2. VISTA PREVIA - Permisos a Migrar' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- Mostrar qué se va a migrar
SELECT 
    r.nombrerol as Rol,
    m.codigo as Codigo_Modulo,
    m.nombre as Nombre_Modulo,
    p.nombre as Proyecto_Destino,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM tbl_proyecto_rol_modulo prm
            WHERE prm.idroles = mp.idroles 
              AND prm.idmodulo = mp.idmodulo 
              AND prm.idproyecto = m.idproyecto
        ) THEN '⚠️ Ya existe'
        ELSE '✅ Se migrará'
    END as Estado
FROM tbl_modulo_permiso mp
JOIN tbl_roles r ON r.idroles = mp.idroles
JOIN tbl_modulo m ON m.idmodulo = mp.idmodulo
JOIN tbl_proyecto p ON p.idproyecto = m.idproyecto
WHERE m.activo = 1
ORDER BY r.nombrerol, m.orden;

-- ============================================================
-- 3. EJECUTAR MIGRACIÓN
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '3. EJECUTANDO MIGRACIÓN...' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- Migrar permisos del sistema antiguo al nuevo
-- Solo migra si el módulo está activo y pertenece a un proyecto
INSERT INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
SELECT DISTINCT
    m.idproyecto,
    mp.idroles,
    mp.idmodulo
FROM tbl_modulo_permiso mp
JOIN tbl_modulo m ON m.idmodulo = mp.idmodulo
WHERE m.activo = 1
  AND m.idproyecto IS NOT NULL
  AND NOT EXISTS (
      -- Evitar duplicados
      SELECT 1 FROM tbl_proyecto_rol_modulo prm
      WHERE prm.idroles = mp.idroles 
        AND prm.idmodulo = mp.idmodulo 
        AND prm.idproyecto = m.idproyecto
  );

SELECT ROW_COUNT() as 'Permisos Migrados';

-- ============================================================
-- 4. VERIFICACIÓN POST-MIGRACIÓN
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '4. VERIFICACIÓN POST-MIGRACIÓN' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- Contar permisos después de la migración
SELECT 
    'Sistema Nuevo (después de migración)' as sistema,
    COUNT(*) as total_permisos,
    COUNT(DISTINCT idroles) as roles_distintos,
    COUNT(DISTINCT idmodulo) as modulos_distintos,
    COUNT(DISTINCT idproyecto) as proyectos_distintos
FROM tbl_proyecto_rol_modulo;

-- Mostrar permisos por rol y proyecto
SELECT 
    p.nombre as Proyecto,
    r.nombrerol as Rol,
    COUNT(DISTINCT prm.idmodulo) as Total_Modulos,
    GROUP_CONCAT(DISTINCT m.codigo ORDER BY m.orden SEPARATOR ', ') as Modulos
FROM tbl_proyecto_rol_modulo prm
JOIN tbl_proyecto p ON p.idproyecto = prm.idproyecto
JOIN tbl_roles r ON r.idroles = prm.idroles
JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
GROUP BY p.nombre, r.nombrerol
ORDER BY p.nombre, r.nombrerol;

-- ============================================================
-- 5. PERMISOS HUÉRFANOS (sin proyecto)
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '5. PERMISOS HUÉRFANOS (módulos sin proyecto)' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- Mostrar permisos que no se pudieron migrar
SELECT 
    r.nombrerol as Rol,
    m.codigo as Codigo_Modulo,
    m.nombre as Nombre_Modulo,
    '⚠️ Sin proyecto asignado' as Problema
FROM tbl_modulo_permiso mp
JOIN tbl_roles r ON r.idroles = mp.idroles
JOIN tbl_modulo m ON m.idmodulo = mp.idmodulo
WHERE m.idproyecto IS NULL OR m.activo = 0
ORDER BY r.nombrerol, m.codigo;

-- ============================================================
-- 6. RECOMENDACIONES
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '6. RECOMENDACIONES' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM tbl_modulo WHERE idproyecto IS NULL AND activo = 1) > 0
        THEN CONCAT('⚠️ Hay ', 
                    (SELECT COUNT(*) FROM tbl_modulo WHERE idproyecto IS NULL AND activo = 1),
                    ' módulos activos sin proyecto asignado')
        ELSE '✅ Todos los módulos activos tienen proyecto asignado'
    END as Check_Modulos,
    CASE 
        WHEN (SELECT COUNT(*) FROM tbl_modulo_permiso) > 
             (SELECT COUNT(*) FROM tbl_proyecto_rol_modulo)
        THEN '⚠️ Hay más permisos en sistema antiguo que en nuevo'
        ELSE '✅ Sistema nuevo tiene igual o más permisos'
    END as Check_Permisos;

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '✅ MIGRACIÓN COMPLETADA' as resultado;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- ============================================================
-- NOTAS IMPORTANTES
-- ============================================================
-- 
-- 1. Este script NO elimina tbl_modulo_permiso (por seguridad)
-- 2. Después de verificar que todo funciona, puedes deprecar la tabla antigua
-- 3. Si hay módulos sin proyecto, asígnalos manualmente antes de migrar
-- 4. Verifica que los usuarios puedan acceder correctamente después de la migración
-- 
-- Para deprecar el sistema antiguo (después de verificar):
-- -- RENAME TABLE tbl_modulo_permiso TO tbl_modulo_permiso_OLD;
-- 
-- ============================================================
