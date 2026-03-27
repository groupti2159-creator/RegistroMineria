from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from extensions import mysql
from utils.helpers import admin_required, modulo_required, get_notif_count, sp_exec, sp_one, md5

admin_bp = Blueprint('admin', __name__)


# ── Configuración — Dashboard ─────────────────────────────────────────────────

@admin_bp.route('/configuracion/dashboard')
@admin_required
@modulo_required('CONFIG_DASH')
def configuracion_dashboard():
    return render_template('configuracion/dashboard.html', notif_count=get_notif_count())


# ── Configuración — Usuarios ──────────────────────────────────────────────────

@admin_bp.route('/configuracion/usuarios')
@admin_required
@modulo_required('CONFIGURACION')
def configuracion_usuarios():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT u.idusuario, u.nombrecompleto, u.correo,
                   CAST(u.activo AS UNSIGNED) AS activo,
                   GROUP_CONCAT(DISTINCT r.nombrerol ORDER BY r.nombrerol SEPARATOR ', ') AS roles,
                   COUNT(DISTINCT ur.idusuariorol) AS cantidadasignaciones
            FROM tbl_usuario u
            LEFT JOIN tbl_usuariorol ur ON ur.idusuario = u.idusuario
            LEFT JOIN tbl_roles r ON r.idroles = ur.idroles
            GROUP BY u.idusuario, u.nombrecompleto, u.correo, u.activo
            ORDER BY u.nombrecompleto
        """)
        usuarios = cur.fetchall()
        cur.close()
        return render_template('configuracion/usuarios.html',
                               usuarios=usuarios,
                               notif_count=get_notif_count())
    except Exception as e:
        import traceback
        return f"<pre>Error: {str(e)}\n{traceback.format_exc()}</pre>", 500


# ── Gestión de Usuarios (Nuevo Sistema - Rutas API) ──────────────────────────

@admin_bp.route('/usuarios/form-data')
@admin_required
def usuarios_form_data():
    try:
        cur = mysql.connection.cursor()
        
        # Proyectos
        cur.execute("SELECT idproyecto, codigo, nombre FROM tbl_proyecto WHERE activo = 1 ORDER BY nombre")
        proyectos = cur.fetchall()
        
        # Roles
        cur.execute("SELECT idroles, nombrerol, descripcion FROM tbl_roles ORDER BY nombrerol")
        roles = cur.fetchall()
        
        # Áreas
        cur.execute("SELECT idarearesponsable, arearesponsable FROM tbl_arearesponsable ORDER BY arearesponsable")
        areas = cur.fetchall()
        
        cur.close()
        
        return jsonify({
            'proyectos': proyectos,
            'roles': roles,
            'areas': areas
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/usuarios/roles')
@admin_required
def usuarios_roles():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT idroles, nombrerol, descripcion FROM tbl_roles ORDER BY nombrerol")
        roles = cur.fetchall()
        cur.close()
        return jsonify(roles)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/usuarios/areas')
@admin_required
def usuarios_areas():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT idarea, nombre AS nombrearea FROM tbl_area WHERE activo = 1 ORDER BY nombre")
        areas = cur.fetchall()
        cur.close()
        return jsonify(areas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/usuarios/modulos/<int:proyecto_id>')
@admin_required
def usuarios_modulos(proyecto_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT idmodulo, idmodulopadre, codigo, nombre, icono, url, orden
            FROM tbl_modulo
            WHERE idproyecto = %s AND activo = 1
            ORDER BY orden
        """, (proyecto_id,))
        modulos = cur.fetchall()
        cur.close()
        
        # Construir jerarquía
        padres = [m for m in modulos if m['idmodulopadre'] is None]
        hijos = [m for m in modulos if m['idmodulopadre'] is not None]
        
        resultado = []
        for padre in padres:
            resultado.append({
                'idModulo': padre['idmodulo'],
                'codigo': padre['codigo'],
                'nombre': padre['nombre'],
                'icono': padre['icono'],
                'hijos': [
                    {
                        'idModulo': h['idmodulo'],
                        'codigo': h['codigo'],
                        'nombre': h['nombre'],
                        'icono': h['icono'],
                        'url': h['url']
                    }
                    for h in hijos if h['idmodulopadre'] == padre['idmodulo']
                ]
            })
        
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/usuarios/crear-nuevo', methods=['POST'])
@admin_required
def usuarios_crear_nuevo():
    """
    Crea un nuevo usuario con sistema de roles puro.
    Los módulos se asignan al ROL, no al usuario individual.
    """
    try:
        data = request.get_json()
        dni = data.get('dni', '').strip()
        nombre = data.get('nombre', '').strip()
        correo = data.get('correo', '').strip() or None
        password = data.get('password', '').strip()
        asignaciones = data.get('asignaciones', [])
        
        if not dni or not nombre or not password:
            return jsonify({'success': False, 'error': 'DNI, nombre y contraseña son requeridos'}), 400
        
        if not asignaciones:
            return jsonify({'success': False, 'error': 'Debe agregar al menos una asignación de proyecto'}), 400
        
        cur = mysql.connection.cursor()
        try:
            # 1. Verificar que el usuario no exista
            cur.execute("SELECT idusuario FROM tbl_usuario WHERE idusuario = %s", (dni,))
            if cur.fetchone():
                return jsonify({'success': False, 'error': 'Ya existe un usuario con ese DNI'}), 400
            
            # 2. Crear usuario
            cur.execute("""
                INSERT INTO tbl_usuario (idusuario, nombrecompleto, correo, contrasena, activo, fechacreacion)
                VALUES (%s, %s, %s, MD5(%s), 1, NOW())
            """, (dni, nombre, correo, password))
            
            # 3. Crear asignaciones (usuario-proyecto-rol)
            for asig in asignaciones:
                proyecto_id = asig.get('proyecto_id')
                rol_id = asig.get('rol_id')
                area_id = asig.get('area_id')
                cargo = asig.get('cargo', '').strip() or None
                
                if not proyecto_id or not rol_id:
                    continue
                
                # Crear asignación usuario-proyecto-rol
                cur.execute("""
                    INSERT INTO tbl_usuariorol (idusuario, idproyecto, idroles, idarea, cargo)
                    VALUES (%s, %s, %s, %s, %s)
                """, (dni, proyecto_id, rol_id, area_id, cargo))
            
            mysql.connection.commit()
            return jsonify({'success': True, 'message': f'Usuario {nombre} creado correctamente'})
            
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'error': f'Error en la transacción: {str(e)}'}), 500
        finally:
            cur.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ── Gestión de Roles y Permisos ──────────────────────────────────────────────

@admin_bp.route('/roles')
@admin_required
# @modulo_required('CONFIGURACION')  # Comentado temporalmente para pruebas
def roles():
    return render_template('admin/roles.html', notif_count=get_notif_count())


@admin_bp.route('/roles/proyectos')
@admin_required
def roles_proyectos():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT idproyecto, codigo, nombre FROM tbl_proyecto WHERE activo = 1 ORDER BY nombre")
        proyectos = cur.fetchall()
        cur.close()
        return jsonify({'proyectos': proyectos})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/roles/proyecto/<int:proyecto_id>/roles')
@admin_required
def roles_proyecto_roles(proyecto_id):
    try:
        cur = mysql.connection.cursor()
        
        # Obtener roles
        cur.execute("SELECT idroles, nombrerol, descripcion FROM tbl_roles ORDER BY nombrerol")
        roles = cur.fetchall()
        
        # Para cada rol, obtener los módulos asignados
        for rol in roles:
            # Obtener módulos asignados a este rol en este proyecto
            cur.execute("""
                SELECT DISTINCT prm.idmodulo
                FROM tbl_proyecto_rol_modulo prm
                WHERE prm.idroles = %s AND prm.idproyecto = %s
            """, (rol['idroles'], proyecto_id))
            
            modulos_asignados = cur.fetchall()
            rol['modulos_ids'] = [m['idmodulo'] for m in modulos_asignados]
            rol['modulos_asignados'] = len(modulos_asignados)
        
        cur.close()
        return jsonify({'roles': roles})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/roles/proyecto/<int:proyecto_id>/modulos')
@admin_required
def roles_proyecto_modulos(proyecto_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT idmodulo, idmodulopadre, codigo, nombre, icono, url, orden
            FROM tbl_modulo
            WHERE idproyecto = %s AND activo = 1
            ORDER BY orden
        """, (proyecto_id,))
        modulos = cur.fetchall()
        cur.close()
        
        # Construir jerarquía
        padres = [m for m in modulos if m['idmodulopadre'] is None]
        hijos = [m for m in modulos if m['idmodulopadre'] is not None]
        
        resultado = []
        for padre in padres:
            resultado.append({
                'idmodulo': padre['idmodulo'],
                'codigo': padre['codigo'],
                'nombre': padre['nombre'],
                'icono': padre['icono'],
                'hijos': [
                    {
                        'idmodulo': h['idmodulo'],
                        'codigo': h['codigo'],
                        'nombre': h['nombre'],
                        'icono': h['icono'],
                        'url': h['url']
                    }
                    for h in hijos if h['idmodulopadre'] == padre['idmodulo']
                ]
            })
        
        return jsonify({'modulos': resultado})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/roles/proyecto/<int:proyecto_id>/rol/<int:rol_id>/permisos', methods=['POST'])
@admin_required
def roles_guardar_permisos(proyecto_id, rol_id):
    try:
        data = request.get_json()
        modulos = data.get('modulos', [])
        
        cur = mysql.connection.cursor()
        try:
            # 1. Eliminar permisos existentes de este rol para este proyecto
            cur.execute("""
                DELETE FROM tbl_proyecto_rol_modulo
                WHERE idroles = %s AND idproyecto = %s
            """, (rol_id, proyecto_id))
            
            # 2. Insertar nuevos permisos
            for modulo_id in modulos:
                # Verificar que el módulo pertenece al proyecto
                cur.execute("""
                    SELECT idmodulo FROM tbl_modulo 
                    WHERE idmodulo = %s AND idproyecto = %s AND activo = 1
                """, (modulo_id, proyecto_id))
                
                if cur.fetchone():
                    cur.execute("""
                        INSERT INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
                        VALUES (%s, %s, %s)
                    """, (proyecto_id, rol_id, modulo_id))
            
            mysql.connection.commit()
            return jsonify({'success': True, 'message': 'Permisos actualizados correctamente'})
            
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'error': f'Error en la transacción: {str(e)}'}), 500
        finally:
            cur.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/roles/crear', methods=['POST'])
@admin_required
def roles_crear():
    try:
        data = request.get_json()
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        
        if not nombre:
            return jsonify({'success': False, 'error': 'El nombre del rol es requerido'}), 400
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                INSERT INTO tbl_roles (nombrerol, descripcion)
                VALUES (%s, %s)
            """, (nombre, descripcion))
            
            mysql.connection.commit()
            return jsonify({'success': True, 'message': 'Rol creado correctamente'})
            
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'error': f'Error al crear rol: {str(e)}'}), 500
        finally:
            cur.close()
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
