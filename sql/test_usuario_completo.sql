-- ============================================================
-- SCRIPT DE PRUEBA COMPLETA DEL SISTEMA DE USUARIOS
-- ============================================================
-- Ejecutar después de fix_sp_modulos_personalizados.sql
-- ============================================================

USE desvios_ambientales;

-- Configurar el DNI del usuario a probar
SET @dni = '12345678';  -- Cambia esto por el DNI del usuario creado

-- ============================================================
-- 1. DATOS DEL USUARIO
-- ============================================================
SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '1. DATOS DEL USUARIO' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

SELECT 
    idusuario as DNI,
    nombrecompleto as Nombre,
    correo as Email,
    CASE activo WHEN 1 THEN '✅ Activo' ELSE '❌ Inactivo' END as Estado
FROM tbl_usuario 
WHERE idusuario = @dni;

-- ============================================================
-- 2. ASIGNACIONES DE ROL Y PROYECTO
-- ============================================================
SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '2. ASIGNACIONES DE ROL Y PROYECTO' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

SELECT 
    ur.idusuariorol as ID_Asignacion,
    p.nombre as Proyecto,
    r.nombrerol as Rol,
    COALESCE(ar.arearesponsable, 'Sin área') as Area,
    COALESCE(ur.cargo, 'Sin cargo') as Cargo
FROM tbl_usuariorol ur
LEFT JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
LEFT JOIN tbl_roles r ON r.idroles = ur.idroles
LEFT JOIN tbl_arearesponsable ar ON ar.idarearesponsable = ur.idarea
WHERE ur.idusuario = @dni;

-- ============================================================
-- 3. MÓDULOS PERSONALIZADOS ASIGNADOS AL USUARIO
-- ============================================================
SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '3. MÓDULOS PERSONALIZADOS DEL USUARIO' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

SELECT 
    ur.idusuariorol as ID_Asignacion,
    p.nombre as Proyecto,
    m.codigo as Codigo_Modulo,
    m.nombre as Nombre_Modulo,
    CASE m.idmodulopadre 
        WHEN NULL THEN '📁 Padre' 
        ELSE '📄 Hijo' 
    END as Tipo,
    CASE ump.permitido 
        WHEN 1 THEN '✅ Permitido' 
        ELSE '❌ Denegado' 
    END as Estado
FROM tbl_usuario_modulo_personalizado ump
JOIN tbl_usuariorol ur ON ur.idusuariorol = ump.idusuariorol
JOIN tbl_modulo m ON m.idmodulo = ump.idmodulo
LEFT JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
WHERE ur.idusuario = @dni
ORDER BY ur.idusuariorol, m.orden;

-- ============================================================
-- 4. MÓDULOS BASE DEL ROL (permisos heredados)
-- ============================================================
SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '4. MÓDULOS BASE DEL ROL (heredados)' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

SELECT 
    r.nombrerol as Rol,
    p.nombre as Proyecto,
    m.codigo as Codigo_Modulo,
    m.nombre as Nombre_Modulo,
    CASE m.idmodulopadre 
        WHEN NULL THEN '📁 Padre' 
        ELSE '📄 Hijo' 
    END as Tipo
FROM tbl_usuariorol ur
JOIN tbl_roles r ON r.idroles = ur.idroles
JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
JOIN tbl_proyecto_rol_modulo prm ON prm.idroles = r.idroles AND prm.idproyecto = p.idproyecto
JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
WHERE ur.idusuario = @dni
ORDER BY p.nombre, m.orden;

-- ============================================================
-- 5. PROBAR STORED PROCEDURE
-- ============================================================
SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '5. RESULTADO DEL STORED PROCEDURE' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- Obtener el idusuariorol para probar
SET @idusuariorol = (SELECT idusuariorol FROM tbl_usuariorol WHERE idusuario = @dni LIMIT 1);

SELECT CONCAT('Probando con idusuariorol = ', @idusuariorol) as info;

CALL sp_obtenermodulospersonalizados(@idusuariorol);

-- ============================================================
-- 6. RESUMEN Y DIAGNÓSTICO
-- ============================================================
SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '6. RESUMEN Y DIAGNÓSTICO' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

SELECT 
    (SELECT COUNT(*) FROM tbl_usuariorol WHERE idusuario = @dni) as Total_Asignaciones,
    (SELECT COUNT(*) 
     FROM tbl_usuario_modulo_personalizado ump
     JOIN tbl_usuariorol ur ON ur.idusuariorol = ump.idusuariorol
     WHERE ur.idusuario = @dni AND ump.permitido = 1) as Modulos_Personalizados,
    (SELECT COUNT(DISTINCT prm.idmodulo)
     FROM tbl_usuariorol ur
     JOIN tbl_proyecto_rol_modulo prm ON prm.idroles = ur.idroles AND prm.idproyecto = ur.idproyecto
     WHERE ur.idusuario = @dni) as Modulos_Del_Rol;

-- ============================================================
-- 7. VERIFICAR SI HAY PROBLEMAS
-- ============================================================
SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '7. VERIFICACIÓN DE PROBLEMAS' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM tbl_usuario WHERE idusuario = @dni) = 0 
        THEN '❌ Usuario no existe'
        ELSE '✅ Usuario existe'
    END as Check_Usuario,
    CASE 
        WHEN (SELECT COUNT(*) FROM tbl_usuariorol WHERE idusuario = @dni) = 0 
        THEN '❌ Sin asignaciones de rol'
        ELSE '✅ Tiene asignaciones'
    END as Check_Asignaciones,
    CASE 
        WHEN (SELECT COUNT(*) 
              FROM tbl_usuario_modulo_personalizado ump
              JOIN tbl_usuariorol ur ON ur.idusuariorol = ump.idusuariorol
              WHERE ur.idusuario = @dni) = 0 
        THEN '⚠️ Sin módulos personalizados (usará permisos del rol)'
        ELSE '✅ Tiene módulos personalizados'
    END as Check_Modulos;

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '✅ PRUEBA COMPLETADA' as resultado;
SELECT '═══════════════════════════════════════════════════' AS separador;
