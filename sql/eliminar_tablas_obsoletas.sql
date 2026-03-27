-- ============================================================
-- ELIMINAR TABLAS OBSOLETAS DEL SISTEMA DE PERMISOS
-- ============================================================
-- Este script elimina las tablas que ya no se usan en el sistema simplificado
-- ADVERTENCIA: Ejecutar solo después de verificar que todo funciona correctamente
-- ============================================================

USE desvios_ambientales;

-- ============================================================
-- 1. ANÁLISIS PREVIO - Ver qué tablas existen
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '1. ANÁLISIS DE TABLAS OBSOLETAS' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- Verificar existencia de tablas obsoletas
SELECT 
    table_name AS Tabla,
    table_rows AS Filas_Aproximadas,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS Tamaño_MB
FROM information_schema.tables
WHERE table_schema = 'desvios_ambientales'
  AND table_name IN ('tbl_modulo_permiso', 'tbl_proyecto_rol_modulo')
ORDER BY table_name;

-- ============================================================
-- 2. BACKUP DE DATOS (por seguridad)
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '2. CREANDO BACKUP DE TABLAS OBSOLETAS' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- Backup de tbl_modulo_permiso
DROP TABLE IF EXISTS tbl_modulo_permiso_BACKUP;
CREATE TABLE IF NOT EXISTS tbl_modulo_permiso_BACKUP AS 
SELECT * FROM tbl_modulo_permiso;

SELECT CONCAT('✅ Backup creado: tbl_modulo_permiso_BACKUP (', 
              COUNT(*), ' registros)') AS resultado
FROM tbl_modulo_permiso_BACKUP;

-- Backup de tbl_proyecto_rol_modulo
DROP TABLE IF EXISTS tbl_proyecto_rol_modulo_BACKUP;
CREATE TABLE IF NOT EXISTS tbl_proyecto_rol_modulo_BACKUP AS 
SELECT * FROM tbl_proyecto_rol_modulo;

SELECT CONCAT('✅ Backup creado: tbl_proyecto_rol_modulo_BACKUP (', 
              COUNT(*), ' registros)') AS resultado
FROM tbl_proyecto_rol_modulo_BACKUP;

-- ============================================================
-- 3. VERIFICAR QUE NO HAY REFERENCIAS EN EL CÓDIGO
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '3. VERIFICACIÓN DE SEGURIDAD' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

SELECT '⚠️ IMPORTANTE: Antes de continuar, verifica que:' AS advertencia
UNION ALL
SELECT '1. El código Python NO usa tbl_modulo_permiso'
UNION ALL
SELECT '2. El código Python NO usa tbl_proyecto_rol_modulo'
UNION ALL
SELECT '3. El sistema funciona correctamente con el nuevo código'
UNION ALL
SELECT '4. Los usuarios pueden hacer login y ver sus módulos'
UNION ALL
SELECT ''
UNION ALL
SELECT '✅ Si todo está verificado, continúa con el siguiente paso';

-- ============================================================
-- 4. ELIMINAR TABLAS OBSOLETAS
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '4. ELIMINANDO TABLAS OBSOLETAS' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- Eliminar tbl_modulo_permiso
DROP TABLE IF EXISTS tbl_modulo_permiso;
SELECT '✅ Tabla tbl_modulo_permiso eliminada' AS resultado;

-- Eliminar tbl_proyecto_rol_modulo
DROP TABLE IF EXISTS tbl_proyecto_rol_modulo;
SELECT '✅ Tabla tbl_proyecto_rol_modulo eliminada' AS resultado;

-- ============================================================
-- 5. VERIFICACIÓN POST-ELIMINACIÓN
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '5. VERIFICACIÓN POST-ELIMINACIÓN' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- Verificar que las tablas ya no existen
SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ tbl_modulo_permiso eliminada correctamente'
        ELSE '❌ tbl_modulo_permiso aún existe'
    END AS estado
FROM information_schema.tables 
WHERE table_schema = 'desvios_ambientales' 
  AND table_name = 'tbl_modulo_permiso';

SELECT 
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ tbl_proyecto_rol_modulo eliminada correctamente'
        ELSE '❌ tbl_proyecto_rol_modulo aún existe'
    END AS estado
FROM information_schema.tables 
WHERE table_schema = 'desvios_ambientales' 
  AND table_name = 'tbl_proyecto_rol_modulo';

-- Verificar que los backups existen
SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN '✅ Backup tbl_modulo_permiso_BACKUP existe'
        ELSE '❌ Backup tbl_modulo_permiso_BACKUP NO existe'
    END AS estado
FROM information_schema.tables 
WHERE table_schema = 'desvios_ambientales' 
  AND table_name = 'tbl_modulo_permiso_BACKUP';

SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN '✅ Backup tbl_proyecto_rol_modulo_BACKUP existe'
        ELSE '❌ Backup tbl_proyecto_rol_modulo_BACKUP NO existe'
    END AS estado
FROM information_schema.tables 
WHERE table_schema = 'desvios_ambientales' 
  AND table_name = 'tbl_proyecto_rol_modulo_BACKUP';

-- ============================================================
-- 6. TABLAS ACTIVAS DEL SISTEMA
-- ============================================================

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '6. TABLAS ACTIVAS DEL SISTEMA DE PERMISOS' as seccion;
SELECT '═══════════════════════════════════════════════════' AS separador;

SELECT 
    table_name AS Tabla_Activa,
    table_rows AS Registros,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS Tamaño_MB
FROM information_schema.tables
WHERE table_schema = 'desvios_ambientales'
  AND table_name IN (
      'tbl_usuario',
      'tbl_usuariorol',
      'tbl_usuario_modulo_personalizado',
      'tbl_modulo',
      'tbl_proyecto',
      'tbl_roles',
      'tbl_arearesponsable'
  )
ORDER BY table_name;

SELECT '═══════════════════════════════════════════════════' AS separador;
SELECT '✅ LIMPIEZA COMPLETADA' as resultado;
SELECT '═══════════════════════════════════════════════════' AS separador;

-- ============================================================
-- NOTAS IMPORTANTES
-- ============================================================
-- 
-- 1. Los backups se mantienen por seguridad:
--    - tbl_modulo_permiso_BACKUP
--    - tbl_proyecto_rol_modulo_BACKUP
-- 
-- 2. Si necesitas restaurar las tablas:
--    CREATE TABLE tbl_modulo_permiso AS SELECT * FROM tbl_modulo_permiso_BACKUP;
--    CREATE TABLE tbl_proyecto_rol_modulo AS SELECT * FROM tbl_proyecto_rol_modulo_BACKUP;
-- 
-- 3. Para eliminar los backups (después de verificar que todo funciona):
--    DROP TABLE tbl_modulo_permiso_BACKUP;
--    DROP TABLE tbl_proyecto_rol_modulo_BACKUP;
-- 
-- 4. Sistema simplificado final:
--    - tbl_usuario (datos básicos)
--    - tbl_usuariorol (contexto: proyecto + rol + área + cargo)
--    - tbl_usuario_modulo_personalizado (permisos personalizados)
--    - tbl_modulo (catálogo de módulos)
--    - tbl_proyecto (catálogo de proyectos)
--    - tbl_roles (catálogo de roles)
--    - tbl_arearesponsable (catálogo de áreas)
-- 
-- ============================================================
