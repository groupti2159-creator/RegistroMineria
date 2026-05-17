import os
import re

filepath = r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\routes\admin.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fijar Seguridad: Añadir @modulo_required('CONFIGURACION') si falta
# Encuentra todos los @admin_required seguidos por def (excluye dashboard que tiene CONFIG_DASH
# y usuarios_form_data - wait, actually the plan says add to all configuracion stuff!
# "Agregado en /usuarios/... y /roles/..."

routes_to_protect = [
    "usuarios_form_data", "usuarios_roles", "usuarios_areas",
    "usuarios_modulos", "usuarios_crear_nuevo", "usuarios_detalle",
    "usuarios_editar", "usuarios_eliminar", "roles", "roles_proyectos",
    "roles_proyecto_roles", "roles_proyecto_modulos", "roles_guardar_permisos",
    "roles_crear", "roles_actualizar", "roles_eliminar"
]

for func in routes_to_protect:
    # Si la función está definida inmediatamente después de @admin_required
    # o si @modulo_required está comentado
    
    # Manejar caso específico del rol comentado
    if func == "roles":
        content = content.replace(
            "@admin_required\n# @modulo_required('CONFIGURACION')  # Comentado temporalmente para pruebas\ndef roles():",
            "@admin_required\n@modulo_required('CONFIGURACION')\ndef roles():"
        )
        continue

    # Para los demás
    pattern = r"(@admin_required\n)def " + func + r"\("
    replacement = r"\1@modulo_required('CONFIGURACION')\ndef " + func + r"("
    content = re.sub(pattern, replacement, content)


# 2. Arreglar Cursores: Hay instancias simples de cur = mysql.cursor()
# Ya que muchos están en try... except... finally cur.close(), veamos cuáles NO están.

# Revisión de usuarios_form_data
v_usuarios_form_data_old = """        cur = mysql.connection.cursor()
        
        # Proyectos
        cur.execute("SELECT idproyecto, nombre, descripcion FROM tbl_proyecto WHERE activo = 1 ORDER BY nombre")
        proyectos = cur.fetchall()
        
        # Roles
        cur.execute("SELECT idroles, nombrerol, descripcion FROM tbl_roles ORDER BY nombrerol")
        roles = cur.fetchall()
        
        # Áreas
        cur.execute("SELECT idarearesponsable, arearesponsable FROM tbl_arearesponsable ORDER BY arearesponsable")
        areas = cur.fetchall()
        
        cur.close()"""

v_usuarios_form_data_new = """        cur = mysql.connection.cursor()
        try:
            # Proyectos
            cur.execute("SELECT idproyecto, nombre, descripcion FROM tbl_proyecto WHERE activo = 1 ORDER BY nombre")
            proyectos = cur.fetchall()
            
            # Roles
            cur.execute("SELECT idroles, nombrerol, descripcion FROM tbl_roles ORDER BY nombrerol")
            roles = cur.fetchall()
            
            # Áreas
            cur.execute("SELECT idarearesponsable, arearesponsable FROM tbl_arearesponsable ORDER BY arearesponsable")
            areas = cur.fetchall()
        finally:
            cur.close()"""

content = content.replace(v_usuarios_form_data_old, v_usuarios_form_data_new)

# usuarios_roles
v_roles_old = """    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT idroles, nombrerol, descripcion FROM tbl_roles ORDER BY nombrerol")
        roles = cur.fetchall()
        cur.close()
        return jsonify(roles)"""

v_roles_new = """    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT idroles, nombrerol, descripcion FROM tbl_roles ORDER BY nombrerol")
            roles = cur.fetchall()
        finally:
            cur.close()
        return jsonify(roles)"""

content = content.replace(v_roles_old, v_roles_new)

# usuarios_areas
v_areas_old = """    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT idarea, nombre AS nombrearea FROM tbl_area WHERE activo = 1 ORDER BY nombre")
        areas = cur.fetchall()
        cur.close()
        return jsonify(areas)"""

v_areas_new = """    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT idarea, nombre AS nombrearea FROM tbl_area WHERE activo = 1 ORDER BY nombre")
            areas = cur.fetchall()
        finally:
            cur.close()
        return jsonify(areas)"""

content = content.replace(v_areas_old, v_areas_new)

# usuarios_modulos
v_modulos_old = """    try:
        cur = mysql.connection.cursor()
        cur.execute(\"""
            SELECT idmodulo, idmodulopadre, codigo, nombre, icono, url, orden
            FROM tbl_modulo
            WHERE idproyecto = %s AND activo = 1
            ORDER BY orden
        \""", (proyecto_id,))
        modulos = cur.fetchall()
        cur.close()"""

v_modulos_new = """    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute(\"""
                SELECT idmodulo, idmodulopadre, codigo, nombre, icono, url, orden
                FROM tbl_modulo
                WHERE idproyecto = %s AND activo = 1
                ORDER BY orden
            \""", (proyecto_id,))
            modulos = cur.fetchall()
        finally:
            cur.close()"""

content = content.replace(v_modulos_old, v_modulos_new)


# usuarios_detalle
v_detalle_old = """    try:
        cur = mysql.connection.cursor()
        usuario = sp_one(cur, 'sp_detalleusuario', (dni,))
        cur.close()

        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

        cur = mysql.connection.cursor()
        asignaciones = sp_exec(cur, 'sp_asignacionesusuario', (dni,))
        cur.close()"""
        
v_detalle_new = """    try:
        cur = mysql.connection.cursor()
        try:
            usuario = sp_one(cur, 'sp_detalleusuario', (dni,))
        finally:
            cur.close()

        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404

        cur = mysql.connection.cursor()
        try:
            asignaciones = sp_exec(cur, 'sp_asignacionesusuario', (dni,))
        finally:
            cur.close()"""
            
content = content.replace(v_detalle_old, v_detalle_new)


# roles_proyectos
v_rproy_old = """    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT idproyecto, nombre, descripcion FROM tbl_proyecto WHERE activo = 1 ORDER BY nombre")
            proyectos = cur.fetchall()
        finally:
            cur.close()
        return jsonify({'proyectos': proyectos})"""
        
v_rproy_new = """    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT idproyecto, nombre, descripcion FROM tbl_proyecto WHERE activo = 1 ORDER BY nombre")
            proyectos = cur.fetchall()
        finally:
            cur.close()
        return jsonify({'proyectos': proyectos})"""
        
content = content.replace(v_rproy_old, v_rproy_new)

# configuracion_usuarios
v_cu_old = """    try:
        cur = mysql.connection.cursor()
        cur.execute(\"""
            SELECT u.idusuario, u.nombrecompleto, u.correo,
                   CAST(u.activo AS UNSIGNED) AS activo,
                   GROUP_CONCAT(DISTINCT r.nombrerol ORDER BY r.nombrerol SEPARATOR ', ') AS roles,
                   COUNT(DISTINCT ur.idusuariorol) AS cantidadasignaciones
            FROM tbl_usuario u
            LEFT JOIN tbl_usuariorol ur ON ur.idusuario = u.idusuario
            LEFT JOIN tbl_roles r ON r.idroles = ur.idroles
            GROUP BY u.idusuario, u.nombrecompleto, u.correo, u.activo
            ORDER BY u.nombrecompleto
        \""")
        usuarios = cur.fetchall()
        cur.close()
        return render_template"""
        
v_cu_new = """    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute(\"""
                SELECT u.idusuario, u.nombrecompleto, u.correo,
                       CAST(u.activo AS UNSIGNED) AS activo,
                       GROUP_CONCAT(DISTINCT r.nombrerol ORDER BY r.nombrerol SEPARATOR ', ') AS roles,
                       COUNT(DISTINCT ur.idusuariorol) AS cantidadasignaciones
                FROM tbl_usuario u
                LEFT JOIN tbl_usuariorol ur ON ur.idusuario = u.idusuario
                LEFT JOIN tbl_roles r ON r.idroles = ur.idroles
                GROUP BY u.idusuario, u.nombrecompleto, u.correo, u.activo
                ORDER BY u.nombrecompleto
            \""")
            usuarios = cur.fetchall()
        finally:
            cur.close()
        return render_template"""

content = content.replace(v_cu_old, v_cu_new)


with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Patched {filepath}")
