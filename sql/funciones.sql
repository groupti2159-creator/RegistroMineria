DELIMITER $

-- SP: Detalle de usuario
DROP PROCEDURE IF EXISTS SP_DetalleUsuario$
CREATE PROCEDURE SP_DetalleUsuario(IN p_dni VARCHAR(20))
BEGIN
    SELECT idusuario, nombrecompleto, correo, activo
    FROM tbl_usuario
    WHERE idusuario = p_dni;
END$

-- SP: Asignaciones del usuario
DROP PROCEDURE IF EXISTS SP_AsignacionesUsuario$
CREATE PROCEDURE SP_AsignacionesUsuario(IN p_dni VARCHAR(20))
BEGIN
    SELECT ur.idusuariorol,
           ur.idproyecto,
           p.codigo AS proyecto_codigo,
           p.nombre AS proyecto_nombre,
           ur.idroles,
           r.nombrerol,
           ur.idarea,
           a.nombre AS area_nombre,
           ur.cargo
    FROM tbl_usuariorol ur
    LEFT JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
    LEFT JOIN tbl_roles r ON r.idroles = ur.idroles
    LEFT JOIN tbl_area a ON a.idarea = ur.idarea
    WHERE ur.idusuario = p_dni;
END$

-- SP: Actualizar usuario
DROP PROCEDURE IF EXISTS SP_ActualizarUsuario$
CREATE PROCEDURE SP_ActualizarUsuario(
    IN p_dni VARCHAR(20),
    IN p_nombre VARCHAR(255),
    IN p_correo VARCHAR(255),
    IN p_activo INT,
    IN p_password VARCHAR(255)
)
BEGIN
    IF p_password IS NULL OR p_password = '' THEN
        UPDATE tbl_usuario
        SET nombrecompleto = p_nombre,
            correo = p_correo,
            activo = p_activo
        WHERE idusuario = p_dni;
    ELSE
        UPDATE tbl_usuario
        SET nombrecompleto = p_nombre,
            correo = p_correo,
            activo = p_activo,
            contrasena = MD5(p_password)
        WHERE idusuario = p_dni;
    END IF;
    SELECT ROW_COUNT() AS affected;
END$

DELIMITER ;