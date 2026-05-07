-- Stored Procedure para obtener personal por área reportante
USE desvios_ambientales;

DELIMITER $$

DROP PROCEDURE IF EXISTS sp_obtener_personal_por_area$$

CREATE PROCEDURE sp_obtener_personal_por_area(
    IN p_idareareportante INT
)
BEGIN
    SELECT 
        id,
        NombresCompletos,
        idareareportante
    FROM tbl_persona
    WHERE idareareportante = p_idareareportante
      AND activo = 1
    ORDER BY NombresCompletos ASC;
END$$

DELIMITER ;
