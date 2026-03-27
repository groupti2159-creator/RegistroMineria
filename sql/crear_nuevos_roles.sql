-- ============================================================
-- CREAR NUEVOS ROLES
-- ============================================================

USE desvios_ambientales;

-- 1. Ver roles existentes
SELECT '========================================' AS '';
SELECT '1. ROLES EXISTENTES' AS '';
SELECT '========================================' AS '';

SELECT * FROM tbl_roles ORDER BY idroles;

-- 2. Ver estructura de la tabla
SELECT '' AS '';
SELECT '========================================' AS '';
SELECT '2. ESTRUCTURA DE LA TABLA' AS '';
SELECT '========================================' AS '';

DESCRIBE tbl_roles;

-- 3. Crear nuevos roles
SELECT '' AS '';
SELECT '========================================' AS '';
SELECT '3. CREANDO NUEVOS ROLES' AS '';
SELECT '========================================' AS '';

-- Rol 1: Ejemplo - Jefe de Área
-- Ajusta el nombre según tus necesidades
INSERT INTO tbl_roles (nombrerol, descripcion)
VALUES ('Jefe de Área', 'Jefe de área con permisos de supervisión y reportes');

-- Rol 2: Ejemplo - Analista
-- Ajusta el nombre según tus necesidades
INSERT INTO tbl_roles (nombrerol, descripcion)
VALUES ('Analista', 'Analista con permisos de consulta y análisis de datos');

SELECT CONCAT('Roles creados: ', ROW_COUNT()) AS '';

-- 4. Ver roles después de la creación
SELECT '' AS '';
SELECT '========================================' AS '';
SELECT '4. ROLES DESPUÉS DE LA CREACIÓN' AS '';
SELECT '========================================' AS '';

SELECT * FROM tbl_roles ORDER BY idroles;

-- 5. Asignar permisos a los nuevos roles
SELECT '' AS '';
SELECT '========================================' AS '';
SELECT '5. ASIGNAR PERMISOS A LOS NUEVOS ROLES' AS '';
SELECT '========================================' AS '';

-- Obtener los IDs de los nuevos roles
SET @jefe_area_id = (SELECT idroles FROM tbl_roles WHERE nombrerol = 'Jefe de Área');
SET @analista_id = (SELECT idroles FROM tbl_roles WHERE nombrerol = 'Analista');

SELECT CONCAT('ID Jefe de Área: ', @jefe_area_id) AS '';
SELECT CONCAT('ID Analista: ', @analista_id) AS '';

-- Ejemplo: Asignar permisos al Jefe de Área
-- Puedes personalizar qué módulos tiene cada rol
SELECT '' AS '';
SELECT 'Asignando permisos a Jefe de Área...' AS '';

INSERT INTO tbl_modulo_permiso (idmodulo, idroles, idarea)
SELECT idmodulo, @jefe_area_id, NULL
FROM tbl_modulo
WHERE codigo IN (
    'DASHBOARD',
    'DESVIOS',
    'ESTADISTICAS',
    'GESTION_RESIDUOS',
    'GENERACION_DIARIA',
    'COMPROMISOS',
    'COMPROMISOS_DASH',
    'MIS_REPORTES'  -- Jefe de Área puede ver sus reportes
);

SELECT CONCAT('Permisos asignados a Jefe de Área: ', ROW_COUNT()) AS '';

-- Ejemplo: Asignar permisos al Analista
SELECT '' AS '';
SELECT 'Asignando permisos a Analista...' AS '';

INSERT INTO tbl_modulo_permiso (idmodulo, idroles, idarea)
SELECT idmodulo, @analista_id, NULL
FROM tbl_modulo
WHERE codigo IN (
    'DASHBOARD',
    'ESTADISTICAS',
    'COMPROMISOS_DASH',
    'AGUAS_DASHBOARD',
    'DATA_METRO_DASH'
    -- Analista solo ve dashboards y estadísticas (solo lectura)
);

SELECT CONCAT('Permisos asignados a Analista: ', ROW_COUNT()) AS '';

-- 6. Verificar permisos asignados
SELECT '' AS '';
SELECT '========================================' AS '';
SELECT '6. VERIFICAR PERMISOS ASIGNADOS' AS '';
SELECT '========================================' AS '';

SELECT '' AS '';
SELECT 'Permisos de Jefe de Área:' AS '';
SELECT m.codigo, m.nombre
FROM tbl_modulo_permiso mp
JOIN tbl_modulo m ON m.idmodulo = mp.idmodulo
WHERE mp.idroles = @jefe_area_id
ORDER BY m.orden;

SELECT '' AS '';
SELECT 'Permisos de Analista:' AS '';
SELECT m.codigo, m.nombre
FROM tbl_modulo_permiso mp
JOIN tbl_modulo m ON m.idmodulo = mp.idmodulo
WHERE mp.idroles = @analista_id
ORDER BY m.orden;

-- 7. Resumen final
SELECT '' AS '';
SELECT '========================================' AS '';
SELECT '7. RESUMEN FINAL' AS '';
SELECT '========================================' AS '';

SELECT 
    r.idroles,
    r.nombrerol,
    COUNT(mp.idmodulo) AS total_modulos
FROM tbl_roles r
LEFT JOIN tbl_modulo_permiso mp ON mp.idroles = r.idroles
GROUP BY r.idroles, r.nombrerol
ORDER BY r.idroles;

SELECT '' AS '';
SELECT '✅ ROLES CREADOS EXITOSAMENTE' AS '';
SELECT '' AS '';
SELECT '📝 NOTAS:' AS '';
SELECT '- Los nombres de los roles son ejemplos, puedes cambiarlos' AS '';
SELECT '- Los permisos asignados son ejemplos, personalízalos según tus necesidades' AS '';
SELECT '- Reinicia la aplicación para que los nuevos roles aparezcan en la interfaz' AS '';
SELECT '- Ahora puedes asignar estos roles a usuarios desde la interfaz web' AS '';
