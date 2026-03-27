-- ============================================================================
-- MIGRACIÓN A SISTEMA PURO POR ROLES (Opción A del documento TablasAcces)
-- ============================================================================
-- Este script migra de un sistema híbrido (roles + personalizados) 
-- a un sistema puro por roles según la propuesta del documento TablasAcces
-- ============================================================================

USE desvios_ambientales;

-- ============================================================================
-- PASO 1: Verificar estructura de tbl_proyecto_rol_modulo
-- ============================================================================
-- Esta tabla es el equivalente a "privilegio_rol_proyecto" del documento

-- Verificar si existe
SELECT 'Verificando tbl_proyecto_rol_modulo...' AS paso;

-- Mostrar estructura actual
DESCRIBE tbl_proyecto_rol_modulo;

-- Mostrar cantidad de registros
SELECT COUNT(*) AS total_permisos_configurados 
FROM tbl_proyecto_rol_modulo;

-- ============================================================================
-- PASO 2: Análisis de datos a migrar
-- ============================================================================
SELECT 'Analizando datos a migrar...' AS paso;

-- Ver cuántos usuarios tienen permisos personalizados
SELECT COUNT(DISTINCT ur.idusuariorol) AS usuarios_con_permisos_personalizados
FROM tbl_usuario_modulo_personalizado ump
JOIN tbl_usuariorol ur ON ur.idusuariorol = ump.idusuariorol;

-- Ver detalle de permisos personalizados por rol
SELECT 
    r.nombrerol,
    p.nombre AS proyecto,
    COUNT(DISTINCT ump.idmodulo) AS modulos_personalizados,
    COUNT(DISTINCT ur.idusuariorol) AS usuarios_afectados
FROM tbl_usuario_modulo_personalizado ump
JOIN tbl_usuariorol ur ON ur.idusuariorol = ump.idusuariorol
JOIN tbl_roles r ON r.idroles = ur.idroles
JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
WHERE ump.permitido = 1
GROUP BY r.nombrerol, p.nombre
ORDER BY r.nombrerol, p.nombre;

-- ============================================================================
-- PASO 3: Migrar permisos personalizados a permisos de rol
-- ============================================================================
SELECT 'Migrando permisos personalizados a sistema de roles...' AS paso;

-- Esta consulta identifica qué módulos están siendo usados por usuarios
-- de cada rol en cada proyecto, y los agrega como permisos del rol

INSERT INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
SELECT DISTINCT 
    ur.idproyecto,
    ur.idroles,
    ump.idmodulo
FROM tbl_usuario_modulo_personalizado ump
JOIN tbl_usuariorol ur ON ur.idusuariorol = ump.idusuariorol
WHERE ump.permitido = 1
  AND NOT EXISTS (
      -- No insertar si ya existe el permiso para ese rol
      SELECT 1 
      FROM tbl_proyecto_rol_modulo prm
      WHERE prm.idproyecto = ur.idproyecto
        AND prm.idroles = ur.idroles
        AND prm.idmodulo = ump.idmodulo
  )
ORDER BY ur.idproyecto, ur.idroles, ump.idmodulo;

-- Mostrar cuántos permisos se agregaron
SELECT ROW_COUNT() AS permisos_migrados;

-- ============================================================================
-- PASO 4: Verificar migración
-- ============================================================================
SELECT 'Verificando migración...' AS paso;

-- Mostrar resumen de permisos por rol después de la migración
SELECT 
    p.nombre AS proyecto,
    r.nombrerol AS rol,
    COUNT(prm.idmodulo) AS total_modulos_permitidos
FROM tbl_proyecto_rol_modulo prm
JOIN tbl_proyecto p ON p.idproyecto = prm.idproyecto
JOIN tbl_roles r ON r.idroles = prm.idroles
GROUP BY p.nombre, r.nombrerol
ORDER BY p.nombre, r.nombrerol;

-- ============================================================================
-- PASO 5: Crear backup de tbl_usuario_modulo_personalizado
-- ============================================================================
SELECT 'Creando backup de tabla antigua...' AS paso;

DROP TABLE IF EXISTS tbl_usuario_modulo_personalizado_backup;

CREATE TABLE tbl_usuario_modulo_personalizado_backup AS
SELECT * FROM tbl_usuario_modulo_personalizado;

SELECT COUNT(*) AS registros_respaldados 
FROM tbl_usuario_modulo_personalizado_backup;

-- ============================================================================
-- PASO 6: Eliminar tabla obsoleta
-- ============================================================================
SELECT 'Eliminando tabla obsoleta...' AS paso;

DROP TABLE IF EXISTS tbl_usuario_modulo_personalizado;

SELECT 'Tabla tbl_usuario_modulo_personalizado eliminada' AS resultado;

-- ============================================================================
-- PASO 7: Verificación final
-- ============================================================================
SELECT 'Verificación final del sistema...' AS paso;

-- Verificar que solo existe el sistema por roles
SELECT 
    'tbl_proyecto_rol_modulo' AS tabla_activa,
    COUNT(*) AS total_permisos
FROM tbl_proyecto_rol_modulo

UNION ALL

SELECT 
    'tbl_usuario_modulo_personalizado_backup' AS tabla_backup,
    COUNT(*) AS total_registros
FROM tbl_usuario_modulo_personalizado_backup;

-- ============================================================================
-- RESUMEN DE LA MIGRACIÓN
-- ============================================================================
SELECT '
╔════════════════════════════════════════════════════════════════╗
║  MIGRACIÓN COMPLETADA - SISTEMA PURO POR ROLES                ║
╠════════════════════════════════════════════════════════════════╣
║  ✓ Permisos personalizados migrados a permisos de rol         ║
║  ✓ Tabla antigua respaldada como _backup                      ║
║  ✓ Sistema ahora usa solo tbl_proyecto_rol_modulo             ║
║                                                                ║
║  SIGUIENTE PASO:                                               ║
║  Actualizar routes/auth.py para usar el nuevo sistema         ║
╚════════════════════════════════════════════════════════════════╝
' AS resumen;

-- ============================================================================
-- NOTAS IMPORTANTES
-- ============================================================================
/*
DESPUÉS DE EJECUTAR ESTE SCRIPT:

1. El sistema ahora funciona 100% por roles
2. Si un usuario necesita permisos especiales, debes:
   - Crear un nuevo rol (ej: "Supervisor Especial")
   - Asignar los módulos a ese rol en tbl_proyecto_rol_modulo
   - Cambiar el rol del usuario en tbl_usuariorol

3. Para restaurar el sistema anterior (si algo sale mal):
   - Renombrar tbl_usuario_modulo_personalizado_backup a tbl_usuario_modulo_personalizado
   - Revertir los cambios en auth.py

4. El backup se puede eliminar después de verificar que todo funciona:
   DROP TABLE tbl_usuario_modulo_personalizado_backup;
*/
