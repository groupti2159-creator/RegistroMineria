-- Ver estructura del módulo CONFIGURACION y sus hijos
SELECT 
    m.idmodulo,
    m.idmodulopadre,
    m.codigo,
    m.nombre,
    m.url,
    m.orden,
    CASE WHEN m.idmodulopadre IS NULL THEN 'PADRE' ELSE 'HIJO' END AS tipo
FROM tbl_modulo m
WHERE m.codigo = 'CONFIGURACION' 
   OR m.idmodulopadre = (SELECT idmodulo FROM tbl_modulo WHERE codigo = 'CONFIGURACION' LIMIT 1)
ORDER BY m.idmodulopadre, m.orden;
