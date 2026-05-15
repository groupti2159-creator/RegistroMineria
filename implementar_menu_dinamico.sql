-- ============================================================================
-- SCRIPT PARA IMPLEMENTAR MENÚ 100% DINÁMICO
-- ============================================================================

-- Seleccionar la base de datos
USE desvios_ambientales;

-- PASO 1: Corregir estructura de módulos (establecer relaciones padre-hijo)
-- ============================================================================

-- Desvíos SSOMA (padre: 25)
UPDATE tbl_modulo SET idmodulopadre = 25 WHERE idmodulo IN (1, 2, 3);

-- Gestión de Residuos (padre: 16)
UPDATE tbl_modulo SET idmodulopadre = 16 WHERE idmodulo IN (17, 18, 19, 20);

-- Compromisos (padre: 30)
UPDATE tbl_modulo SET idmodulopadre = 30 WHERE idmodulo IN (26, 29);

-- Data Meteorológica (padre: 32)
UPDATE tbl_modulo SET idmodulopadre = 32 WHERE idmodulo IN (27, 31);

-- Configuración (padre: 4)
UPDATE tbl_modulo SET idmodulopadre = 4 WHERE idmodulo IN (28, 45);

-- Gestión de Aguas (padre: 33)
UPDATE tbl_modulo SET idmodulopadre = 33 WHERE idmodulo IN (34, 35, 36);


-- PASO 2: Actualizar nombres de módulos padre
-- ============================================================================

UPDATE tbl_modulo SET nombre = 'Desvíos SSOMA' WHERE idmodulo = 25;
UPDATE tbl_modulo SET nombre = 'Gestión de Residuos' WHERE idmodulo = 16;
UPDATE tbl_modulo SET nombre = 'Compromisos' WHERE idmodulo = 30;
UPDATE tbl_modulo SET nombre = 'Data Meteorológica' WHERE idmodulo = 32;
UPDATE tbl_modulo SET nombre = 'Configuración' WHERE idmodulo = 4;
UPDATE tbl_modulo SET nombre = 'Gestión de Aguas' WHERE idmodulo = 33;


-- PASO 3: Eliminar módulos duplicados
-- ============================================================================

-- Eliminar módulo duplicado DESVIOS (id=62)
DELETE FROM tbl_proyecto_rol_modulo WHERE idmodulo = 62;
DELETE FROM tbl_modulo WHERE idmodulo = 62;


-- PASO 4: Verificar estructura
-- ============================================================================

SELECT 
    CONCAT('PADRE: ', m.nombre) as tipo,
    m.idmodulo,
    m.codigo,
    m.nombre,
    m.icono,
    m.orden
FROM tbl_modulo m
WHERE m.idmodulopadre IS NULL
ORDER BY m.orden;

SELECT 
    CONCAT('  └─ HIJO: ', h.nombre) as tipo,
    h.idmodulo,
    h.codigo,
    h.nombre,
    h.url,
    p.nombre as padre
FROM tbl_modulo h
JOIN tbl_modulo p ON p.idmodulo = h.idmodulopadre
ORDER BY p.orden, h.orden;


-- ============================================================================
-- EJEMPLOS DE USO DESPUÉS DE IMPLEMENTAR
-- ============================================================================

-- Cambiar "Desvíos SSOMA" a otro nombre:
-- UPDATE tbl_modulo SET nombre = 'Desvíos Ambientales' WHERE idmodulo = 25;

-- Cambiar icono de un grupo:
-- UPDATE tbl_modulo SET icono = 'shield' WHERE idmodulo = 25;

-- Agregar nuevo submódulo a "Desvíos SSOMA":
-- INSERT INTO tbl_modulo (codigo, nombre, icono, url, orden, idmodulopadre, activo)
-- VALUES ('NUEVO_MODULO', 'Nuevo Módulo', 'star', '/admin/nuevo', 1, 25, 1);

-- Cambiar orden de aparición de grupos:
-- UPDATE tbl_modulo SET orden = 5 WHERE idmodulo = 25;  -- Mover Desvíos SSOMA
