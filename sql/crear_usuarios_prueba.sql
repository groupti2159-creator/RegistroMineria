-- ============================================================================
-- CREAR USUARIOS DE PRUEBA PARA CADA ROL
-- ============================================================================
-- Crea 3 usuarios de prueba: Administrador, Supervisor y Trabajador
-- Contraseña para todos: 123456 (MD5: e10adc3949ba59abbe56e057f20f883e)
-- ============================================================================

-- Verificar que no existan
DELETE FROM tbl_usuariorol WHERE idusuario IN ('11111111', '22222222', '33333333');
DELETE FROM tbl_usuario WHERE idusuario IN ('11111111', '22222222', '33333333');

-- Insertar usuarios
INSERT INTO tbl_usuario (idusuario, nombrecompleto, correo, contrasena, activo, fechacreacion)
VALUES 
    ('11111111', 'Admin Prueba', 'admin@test.com', 'e10adc3949ba59abbe56e057f20f883e', 1, NOW()),
    ('22222222', 'Supervisor Prueba', 'supervisor@test.com', 'e10adc3949ba59abbe56e057f20f883e', 1, NOW()),
    ('33333333', 'Trabajador Prueba', 'trabajador@test.com', 'e10adc3949ba59abbe56e057f20f883e', 1, NOW());

-- Asignar roles (asumiendo que el proyecto 1 existe)
INSERT INTO tbl_usuariorol (idusuario, idproyecto, idroles, idarea, cargo)
VALUES 
    ('11111111', 1, 1, NULL, 'Administrador del Sistema'),  -- Administrador
    ('22222222', 1, 2, NULL, 'Supervisor de Campo'),         -- Supervisor
    ('33333333', 1, 3, NULL, 'Trabajador de Campo');         -- Trabajador

-- Verificar inserción
SELECT 
    u.idusuario AS DNI,
    u.nombrecompleto AS Nombre,
    r.nombrerol AS Rol,
    p.nombre AS Proyecto,
    '123456' AS Password
FROM tbl_usuario u
JOIN tbl_usuariorol ur ON ur.idusuario = u.idusuario
JOIN tbl_roles r ON r.idroles = ur.idroles
LEFT JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
WHERE u.idusuario IN ('11111111', '22222222', '33333333')
ORDER BY r.idroles;
