-- Diagnóstico de usuario recién creado
-- Reemplaza 'TU_DNI' con el DNI del usuario que creaste

SET @dni = 'TU_DNI';  -- Cambia esto por el DNI real

-- 1. Ver datos del usuario
SELECT 'DATOS DEL USUARIO' as seccion;
SELECT * FROM tbl_usuario WHERE idusuario = @dni;

-- 2. Ver asignaciones de rol
SELECT 'ASIGNACIONES DE ROL' as seccion;
SELECT 
    ur.idusuariorol,
    ur.idusuario,
    p.nombre as proyecto,
    r.nombrerol as rol,
    ar.arearesponsable as area,
    ur.cargo
FROM tbl_usuariorol ur
LEFT JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
LEFT JOIN tbl_roles r ON r.idroles = ur.idroles
LEFT JOIN tbl_arearesponsable ar ON ar.idarearesponsable = ur.idarea
WHERE ur.idusuario = @dni;

-- 3. Ver módulos personalizados asignados
SELECT 'MÓDULOS PERSONALIZADOS' as seccion;
SELECT 
    ump.idusuariorol,
    m.codigo,
    m.nombre as modulo,
    ump.permitido
FROM tbl_usuario_modulo_personalizado ump
JOIN tbl_modulo m ON m.idmodulo = ump.idmodulo
WHERE ump.idusuariorol IN (
    SELECT idusuariorol FROM tbl_usuariorol WHERE idusuario = @dni
);

-- 4. Ver módulos del ROL asignado (permisos base del rol)
SELECT 'MÓDULOS DEL ROL' as seccion;
SELECT 
    r.nombrerol,
    p.nombre as proyecto,
    m.codigo,
    m.nombre as modulo
FROM tbl_usuariorol ur
JOIN tbl_roles r ON r.idroles = ur.idroles
JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
JOIN tbl_proyecto_rol_modulo prm ON prm.idroles = r.idroles AND prm.idproyecto = p.idproyecto
JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
WHERE ur.idusuario = @dni;

-- 5. Probar el stored procedure
SELECT 'RESULTADO DEL SP' as seccion;
CALL sp_obtenermodulospersonalizados(5);  -- Cambia 5 por el idusuariorol correcto
