from flask import render_template, request, jsonify
from extensions import mysql
from utils.helpers import admin_required, get_notif_count
from routes.configuracion import admin_bp


@admin_bp.route('/roles')
@admin_required
def roles():
    return render_template('configuracion/roles.html', notif_count=get_notif_count())


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
        cur.execute("SELECT idroles, nombrerol, descripcion FROM tbl_roles ORDER BY nombrerol")
        roles_list = cur.fetchall()
        for rol in roles_list:
            cur.execute("""
                SELECT DISTINCT prm.idmodulo
                FROM tbl_proyecto_rol_modulo prm
                WHERE prm.idroles = %s AND prm.idproyecto = %s
            """, (rol['idroles'], proyecto_id))
            modulos_asignados = cur.fetchall()
            rol['modulos_ids']      = [m['idmodulo'] for m in modulos_asignados]
            rol['modulos_asignados'] = len(modulos_asignados)
        cur.close()
        return jsonify({'roles': roles_list})
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
        padres = [m for m in modulos if m['idmodulopadre'] is None]
        hijos  = [m for m in modulos if m['idmodulopadre'] is not None]
        resultado = []
        for padre in padres:
            resultado.append({
                'idmodulo': padre['idmodulo'], 'codigo': padre['codigo'],
                'nombre':   padre['nombre'],   'icono':  padre['icono'],
                'hijos': [{'idmodulo': h['idmodulo'], 'codigo': h['codigo'],
                           'nombre': h['nombre'], 'icono': h['icono'], 'url': h['url']}
                          for h in hijos if h['idmodulopadre'] == padre['idmodulo']]
            })
        return jsonify({'modulos': resultado})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/roles/proyecto/<int:proyecto_id>/rol/<int:rol_id>/permisos', methods=['POST'])
@admin_required
def roles_guardar_permisos(proyecto_id, rol_id):
    try:
        data    = request.get_json()
        modulos = data.get('modulos', [])
        cur = mysql.connection.cursor()
        try:
            cur.execute("DELETE FROM tbl_proyecto_rol_modulo WHERE idroles = %s AND idproyecto = %s", (rol_id, proyecto_id))
            for modulo_id in modulos:
                cur.execute("SELECT idmodulo FROM tbl_modulo WHERE idmodulo = %s AND idproyecto = %s AND activo = 1", (modulo_id, proyecto_id))
                if cur.fetchone():
                    cur.execute("INSERT INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo) VALUES (%s, %s, %s)", (proyecto_id, rol_id, modulo_id))
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
        data        = request.get_json()
        nombre      = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        if not nombre:
            return jsonify({'success': False, 'error': 'El nombre del rol es requerido'}), 400
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO tbl_roles (nombrerol, descripcion) VALUES (%s, %s)", (nombre, descripcion))
            mysql.connection.commit()
            return jsonify({'success': True, 'message': 'Rol creado correctamente'})
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'error': f'Error al crear rol: {str(e)}'}), 500
        finally:
            cur.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/roles/<int:rol_id>/actualizar', methods=['PUT'])
@admin_required
def roles_actualizar(rol_id):
    try:
        data        = request.get_json()
        nombre      = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        if not nombre:
            return jsonify({'success': False, 'error': 'El nombre del rol es requerido'}), 400
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT idroles FROM tbl_roles WHERE idroles = %s", (rol_id,))
            if not cur.fetchone():
                return jsonify({'success': False, 'error': 'Rol no encontrado'}), 404
            cur.execute("UPDATE tbl_roles SET nombrerol = %s, descripcion = %s WHERE idroles = %s", (nombre, descripcion, rol_id))
            mysql.connection.commit()
            return jsonify({'success': True, 'message': 'Rol actualizado correctamente'})
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'error': f'Error al actualizar rol: {str(e)}'}), 500
        finally:
            cur.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/roles/<int:rol_id>/eliminar', methods=['DELETE'])
@admin_required
def roles_eliminar(rol_id):
    try:
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT idroles, nombrerol FROM tbl_roles WHERE idroles = %s", (rol_id,))
            rol = cur.fetchone()
            if not rol:
                return jsonify({'success': False, 'error': 'Rol no encontrado'}), 404
            cur.execute("SELECT COUNT(*) as count FROM tbl_usuariorol WHERE idroles = %s", (rol_id,))
            count = cur.fetchone()['count']
            if count > 0:
                return jsonify({'success': False,
                    'error': f'No se puede eliminar el rol porque tiene {count} usuario(s) asignado(s).'}), 400
            cur.execute("DELETE FROM tbl_proyecto_rol_modulo WHERE idroles = %s", (rol_id,))
            cur.execute("DELETE FROM tbl_roles WHERE idroles = %s", (rol_id,))
            mysql.connection.commit()
            return jsonify({'success': True, 'message': f'Rol "{rol["nombrerol"]}" eliminado correctamente'})
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'error': f'Error al eliminar rol: {str(e)}'}), 500
        finally:
            cur.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
