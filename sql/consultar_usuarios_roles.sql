-- ============================================================================
-- CONSULTAR USUARIOS Y SUS ROLES
-- ============================================================================
-- Script para ver todos los usuarios con sus roles asignados
-- ============================================================================

-- Ver todos los usuarios activos
SELECT 
    u.idusuario AS DNI,
    u.nombrecompleto AS Nombre,
    u.correo AS Email,
    u.activo AS Activo
FROM tbl_usuario u
ORDER BY u.idusuario;

-- Ver usuarios con sus roles y proyectos
SELECT 
    u.idusuario AS DNI,
    u.nombrecompleto AS Nombre,
    r.nombrerol AS Rol,
    p.nombre AS Proyecto,
    ur.cargo AS Cargo,
    a.nombre AS Area
FROM tbl_usuario u
JOIN tbl_usuariorol ur ON ur.idusuario = u.idusuario
JOIN tbl_roles r ON r.idroles = ur.idroles
LEFT JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
LEFT JOIN tbl_area a ON a.idarea = ur.idarea
WHERE u.activo = 1
ORDER BY r.idroles, u.idusuario;

-- Ver contraseñas (MD5 hash) para referencia
SELECT 
    u.idusuario AS DNI,
    u.nombrecompleto AS Nombre,
    u.contrasena AS Password_MD5,
    CASE 
        WHEN u.contrasena = 'e10adc3949ba59abbe56e057f20f883e' THEN '123456'
        WHEN u.contrasena = '0192023a7bbd73250516f069df18b500' THEN 'admin'
        WHEN u.contrasena = '5f4dcc3b5aa765d61d8327deb882cf99' THEN 'password'
        ELSE 'desconocido'
    END AS Password_Texto
FROM tbl_usuario u
WHERE u.activo = 1;
