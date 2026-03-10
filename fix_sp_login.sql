-- Corregir el stored procedure sp_login para usar tablas en minúsculas
-- Compatible con Railway (Linux/MySQL case-sensitive)

DROP PROCEDURE IF EXISTS sp_login;

DELIMITER $$

CREATE PROCEDURE sp_login(
    IN p_dni VARCHAR(20),
    IN p_pass VARCHAR(255)
)
BEGIN
    SELECT u.idUsuario, u.DNI, u.NombreCompleto, u.Correo, u.Activo,
           ur.IdUsuarioRol, r.idRoles, r.NombreRol
    FROM tbl_usuario u
    JOIN tbl_usuariorol ur ON ur.idUsuario = u.idUsuario
    JOIN tbl_roles r ON r.idRoles = ur.idRoles
    WHERE u.DNI = p_dni
      AND u.Contrasena = MD5(p_pass)
      AND u.Activo = 1
    LIMIT 1;
END$$

DELIMITER ;
