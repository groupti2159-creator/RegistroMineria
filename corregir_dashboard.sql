-- ============================================================================
-- CORREGIR MÓDULO DASHBOARD
-- ============================================================================

USE desvios_ambientales;

-- El módulo DASHBOARD debe:
-- 1. Ser hijo de DESVIOS_AMB (idmodulopadre = 25)
-- 2. Tener URL = /admin/dashboard
-- 3. Tener icono apropiado

UPDATE tbl_modulo 
SET 
    idmodulopadre = 25,
    url = '/admin/dashboard',
    icono = 'home',
    nombre = 'Dashboard'
WHERE idmodulo = 1;

-- Verificar el cambio
SELECT 
    m.idmodulo,
    m.codigo,
    m.nombre,
    m.url,
    m.icono,
    m.idmodulopadre,
    p.nombre as nombre_padre
FROM tbl_modulo m
LEFT JOIN tbl_modulo p ON p.idmodulo = m.idmodulopadre
WHERE m.idmodulo = 1;

-- Ver todos los hijos de DESVIOS_AMB
SELECT 
    m.idmodulo,
    m.codigo,
    m.nombre,
    m.url,
    m.icono,
    m.orden
FROM tbl_modulo m
WHERE m.idmodulopadre = 25
ORDER BY m.orden;
