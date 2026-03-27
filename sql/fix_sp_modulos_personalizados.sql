-- ============================================================
-- FIX: Stored Procedure para Módulos Personalizados
-- ============================================================
-- Crea el SP correcto para cargar módulos personalizados
-- ============================================================

USE desvios_ambientales;

DELIMITER $$

-- Eliminar y recrear el stored procedure
DROP PROCEDURE IF EXISTS sp_obtenermodulospersonalizados$$

CREATE PROCEDURE sp_obtenermodulospersonalizados(IN p_usuario_rol INT)
BEGIN
    -- Obtener módulos personalizados del usuario con información completa
    -- Incluye jerarquía (padres e hijos) para construir el menú lateral
    SELECT 
        m.idmodulo, 
        m.idmodulopadre, 
        m.codigo, 
        m.nombre, 
        m.icono, 
        m.url, 
        m.orden
    FROM tbl_modulo m
    INNER JOIN tbl_usuario_modulo_personalizado ump 
        ON ump.idmodulo = m.idmodulo
    WHERE ump.idusuariorol = p_usuario_rol 
      AND ump.permitido = 1
      AND m.activo = 1
    ORDER BY m.orden;
END$$

DELIMITER ;

-- ============================================================
-- Verificar que el SP se creó correctamente
-- ============================================================

SELECT '✅ Stored procedure sp_obtenermodulospersonalizados creado correctamente' AS resultado;

-- Ver la definición
SHOW CREATE PROCEDURE sp_obtenermodulospersonalizados;

SELECT '✅ Sistema simplificado listo' AS estado;
