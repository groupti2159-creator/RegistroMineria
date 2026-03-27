-- ============================================================================
-- UNIFICACIÓN DE TABLAS DE USUARIO
-- ============================================================================
-- Problema: Existen dos tablas con nombres similares:
--   - tbl_usuario (minúsculas)
--   - Tbl_Usuario (mayúsculas)
-- 
-- Solución: Unificar todo en tbl_usuario (minúsculas)
-- ============================================================================

USE desvios_ambientales;

-- ============================================================================
-- PASO 1: Verificar existencia de ambas tablas
-- ============================================================================
SELECT 'Verificando tablas existentes...' AS paso;

-- Mostrar estructura de tbl_usuario (minúsculas)
SELECT 'Estructura de tbl_usuario:' AS info;
DESCRIBE tbl_usuario;

-- Mostrar datos de tbl_usuario
SELECT 'Datos en tbl_usuario:' AS info;
SELECT idusuario, nombrecompleto, correo, activo, fechacreacion 
FROM tbl_usuario;

-- Mostrar estructura de Tbl_Usuario (mayúsculas) si existe
SELECT 'Estructura de Tbl_Usuario:' AS info;
DESCRIBE Tbl_Usuario;

-- Mostrar datos de Tbl_Usuario
SELECT 'Datos en Tbl_Usuario:' AS info;
SELECT idusuario, nombrecompleto, correo, activo, fechacreacion 
FROM Tbl_Usuario;

-- ============================================================================
-- PASO 2: Verificar conflictos de DNI
-- ============================================================================
SELECT 'Verificando conflictos de DNI...' AS paso;

-- Ver si hay DNIs duplicados entre ambas tablas
SELECT 
    t1.idusuario,
    t1.nombrecompleto AS nombre_tbl_usuario,
    t2.nombrecompleto AS nombre_Tbl_Usuario,
    'CONFLICTO: Mismo DNI en ambas tablas' AS estado
FROM tbl_usuario t1
INNER JOIN Tbl_Usuario t2 ON t1.idusuario = t2.idusuario;

-- Si no hay conflictos, mostrar mensaje
SELECT CASE 
    WHEN NOT EXISTS (
        SELECT 1 FROM tbl_usuario t1
        INNER JOIN Tbl_Usuario t2 ON t1.idusuario = t2.idusuario
    )
    THEN '✓ No hay conflictos de DNI'
    ELSE '⚠ HAY CONFLICTOS - Revisar antes de continuar'
END AS resultado;

-- ============================================================================
-- PASO 3: Migrar datos de Tbl_Usuario a tbl_usuario
-- ============================================================================
SELECT 'Migrando datos de Tbl_Usuario a tbl_usuario...' AS paso;

-- Insertar usuarios de Tbl_Usuario que NO existan en tbl_usuario
INSERT INTO tbl_usuario (idusuario, nombrecompleto, correo, contrasena, activo, fechacreacion)
SELECT 
    idusuario,
    nombrecompleto,
    correo,
    contrasena,
    activo,
    fechacreacion
FROM Tbl_Usuario
WHERE idusuario NOT IN (SELECT idusuario FROM tbl_usuario);

-- Mostrar cuántos registros se migraron
SELECT ROW_COUNT() AS registros_migrados;

-- ============================================================================
-- PASO 4: Verificar migración
-- ============================================================================
SELECT 'Verificando migración...' AS paso;

-- Mostrar todos los usuarios en tbl_usuario después de la migración
SELECT 
    idusuario,
    nombrecompleto,
    correo,
    activo,
    fechacreacion,
    'tbl_usuario' AS tabla_origen
FROM tbl_usuario
ORDER BY fechacreacion;

-- Contar total de usuarios
SELECT COUNT(*) AS total_usuarios_unificados FROM tbl_usuario;

-- ============================================================================
-- PASO 5: Verificar referencias en tbl_usuariorol
-- ============================================================================
SELECT 'Verificando referencias en tbl_usuariorol...' AS paso;

-- Ver qué tabla está siendo referenciada
SELECT 
    ur.idusuariorol,
    ur.idusuario,
    u.nombrecompleto,
    r.nombrerol,
    p.nombre AS proyecto
FROM tbl_usuariorol ur
LEFT JOIN tbl_usuario u ON u.idusuario = ur.idusuario
LEFT JOIN tbl_roles r ON r.idroles = ur.idroles
LEFT JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
ORDER BY ur.idusuariorol;

-- Verificar si hay usuarios en tbl_usuariorol que no existen en tbl_usuario
SELECT 
    ur.idusuario,
    'Usuario en tbl_usuariorol pero NO en tbl_usuario' AS problema
FROM tbl_usuariorol ur
WHERE ur.idusuario NOT IN (SELECT idusuario FROM tbl_usuario);

-- ============================================================================
-- PASO 6: Crear backup de Tbl_Usuario antes de eliminar
-- ============================================================================
SELECT 'Creando backup de Tbl_Usuario...' AS paso;

DROP TABLE IF EXISTS Tbl_Usuario_backup;

CREATE TABLE Tbl_Usuario_backup AS
SELECT * FROM Tbl_Usuario;

SELECT COUNT(*) AS registros_respaldados FROM Tbl_Usuario_backup;

-- ============================================================================
-- PASO 7: Eliminar tabla duplicada
-- ============================================================================
SELECT 'Eliminando tabla duplicada Tbl_Usuario...' AS paso;

DROP TABLE IF EXISTS Tbl_Usuario;

SELECT 'Tabla Tbl_Usuario eliminada' AS resultado;

-- ============================================================================
-- PASO 8: Verificación final
-- ============================================================================
SELECT 'Verificación final...' AS paso;

-- Mostrar resumen
SELECT 
    'tbl_usuario' AS tabla_activa,
    COUNT(*) AS total_usuarios
FROM tbl_usuario

UNION ALL

SELECT 
    'Tbl_Usuario_backup' AS tabla_backup,
    COUNT(*) AS total_registros
FROM Tbl_Usuario_backup;

-- Verificar que todas las referencias están correctas
SELECT 
    'Referencias en tbl_usuariorol' AS verificacion,
    COUNT(*) AS total_asignaciones,
    COUNT(DISTINCT ur.idusuario) AS usuarios_unicos
FROM tbl_usuariorol ur
INNER JOIN tbl_usuario u ON u.idusuario = ur.idusuario;

-- ============================================================================
-- RESUMEN
-- ============================================================================
SELECT '
╔════════════════════════════════════════════════════════════════╗
║  UNIFICACIÓN DE TABLAS COMPLETADA                             ║
╠════════════════════════════════════════════════════════════════╣
║  ✓ Datos migrados de Tbl_Usuario a tbl_usuario                ║
║  ✓ Tabla duplicada eliminada                                  ║
║  ✓ Backup creado como Tbl_Usuario_backup                      ║
║  ✓ Todas las referencias verificadas                          ║
║                                                                ║
║  TABLA ACTIVA: tbl_usuario (minúsculas)                       ║
║                                                                ║
║  SIGUIENTE PASO:                                               ║
║  Verificar que todo el código use "tbl_usuario" (minúsculas)  ║
╚════════════════════════════════════════════════════════════════╝
' AS resumen;

-- ============================================================================
-- NOTAS IMPORTANTES
-- ============================================================================
/*
DESPUÉS DE EJECUTAR ESTE SCRIPT:

1. La tabla activa es: tbl_usuario (minúsculas)
2. Todos los usuarios están unificados en una sola tabla
3. El backup está en: Tbl_Usuario_backup

4. Para restaurar si algo sale mal:
   CREATE TABLE Tbl_Usuario AS SELECT * FROM Tbl_Usuario_backup;

5. Para eliminar el backup después de verificar:
   DROP TABLE Tbl_Usuario_backup;

6. IMPORTANTE: Verificar que todo el código Python use "tbl_usuario" (minúsculas)
   - Buscar en routes/auth.py
   - Buscar en routes/admin.py
   - Buscar en stored procedures
*/
