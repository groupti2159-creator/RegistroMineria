from flask import render_template, request, jsonify
from extensions import mysql
from utils.helpers import admin_required, modulo_required, get_notif_count, sp_exec, sp_one
from routes.configuracion import admin_bp


def _borrar_notificaciones_por_usuariorol(cur, ids):
    """Elimina notificaciones ligadas a filas de tbl_usuariorol."""
    if not ids:
        return
    ph = ','.join(['%s'] * len(ids))
    cur.execute(f'DELETE FROM tbl_notificacion WHERE idusuariorol IN ({ph})', tuple(ids))


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
                               usuarios=usuarios, notif_count=get_notif_count())
    except Exception as e:
        import traceback
        return f"<pre>Error: {str(e)}\n{traceback.format_exc()}</pre>", 500


@admin_bp.route('/usuarios/form-data')
@admin_required
def usuarios_form_data():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT idproyecto, codigo, nombre FROM tbl_proyecto WHERE activo = 1 ORDER BY nombre")
        proyectos = cur.fetchall()
        cur.execute("SELECT idroles, nombrerol, descripcion FROM tbl_roles ORDER BY nombrerol")
        roles = cur.fetchall()
        cur.execute("SELECT idarearesponsable, arearesponsable FROM tbl_arearesponsable ORDER BY arearesponsable")
        areas = cur.fetchall()
        cur.close()
        return jsonify({'proyectos': proyectos, 'roles': roles, 'areas': areas})
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
        padres = [m for m in modulos if m['idmodulopadre'] is None]
        hijos  = [m for m in modulos if m['idmodulopadre'] is not None]
        resultado = []
        for padre in padres:
            resultado.append({
                'idModulo': padre['idmodulo'], 'codigo': padre['codigo'],
                'nombre':   padre['nombre'],   'icono':  padre['icono'],
                'hijos': [{'idModulo': h['idmodulo'], 'codigo': h['codigo'],
                           'nombre': h['nombre'], 'icono': h['icono'], 'url': h['url']}
                          for h in hijos if h['idmodulopadre'] == padre['idmodulo']]
            })
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/usuarios/crear-nuevo', methods=['POST'])
@admin_required
def usuarios_crear_nuevo():
    try:
        data        = request.get_json()
        dni         = data.get('dni', '').strip()
        nombre      = data.get('nombre', '').strip()
        correo      = data.get('correo', '').strip() or None
        password    = data.get('password', '').strip()
        asignaciones = data.get('asignaciones', [])

        if not dni or not nombre or not password:
            return jsonify({'success': False, 'error': 'DNI, nombre y contraseña son requeridos'}), 400
        if not asignaciones:
            return jsonify({'success': False, 'error': 'Debe agregar al menos una asignación de proyecto'}), 400

        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT idusuario FROM tbl_usuario WHERE idusuario = %s", (dni,))
            if cur.fetchone():
                return jsonify({'success': False, 'error': 'Ya existe un usuario con ese DNI'}), 400
            cur.execute("""
                INSERT INTO tbl_usuario (idusuario, nombrecompleto, correo, contrasena, activo, fechacreacion)
                VALUES (%s, %s, %s, MD5(%s), 1, NOW())
            """, (dni, nombre, correo, password))
            for asig in asignaciones:
                proyecto_id = asig.get('proyecto_id')
                rol_id      = asig.get('rol_id')
                if not proyecto_id or not rol_id:
                    continue
                cur.execute("""
                    INSERT INTO tbl_usuariorol (idusuario, idproyecto, idroles, idarea, cargo)
                    VALUES (%s, %s, %s, %s, %s)
                """, (dni, proyecto_id, rol_id, asig.get('area_id'), asig.get('cargo', '').strip() or None))
            mysql.connection.commit()
            return jsonify({'success': True, 'message': f'Usuario {nombre} creado correctamente'})
        except Exception as e:
            mysql.connection.rollback()
            return jsonify({'success': False, 'error': f'Error en la transacción: {str(e)}'}), 500
        finally:
            cur.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/usuarios/detalle/<dni>')
@admin_required
def usuarios_detalle(dni):
    try:
        cur = mysql.connection.cursor()
        usuario     = sp_one(cur, 'sp_detalleusuario', (dni,))
        cur.close()
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404
        cur = mysql.connection.cursor()
        asignaciones = sp_exec(cur, 'sp_asignacionesusuario', (dni,))
        cur.close()

        def serialize(row):
            if row is None: return {}
            return {k.lower(): (v.strftime('%Y-%m-%d') if hasattr(v, 'strftime') else (v if v is not None else ''))
                    for k, v in row.items()}

        return jsonify({'success': True, 'usuario': serialize(usuario),
                        'asignaciones': [serialize(a) for a in asignaciones]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/usuarios/editar/<dni>', methods=['POST'])
@admin_required
def usuarios_editar(dni):
    try:
        data     = request.get_json() or {}
        nombre   = data.get('nombre', '').strip()
        correo   = data.get('correo') or None
        if isinstance(correo, str): correo = correo.strip() or None
        activo   = int(data.get('activo', 1))
        password = data.get('password', '').strip()

        if not nombre:
            return jsonify({'success': False, 'error': 'El nombre completo es requerido'}), 400

        cur = mysql.connection.cursor()
        try:
            cur.execute("CALL SP_ActualizarUsuario(%s, %s, %s, %s, %s)",
                        (dni, nombre, correo, activo, password or None))
            cur.fetchall()
            while cur.nextset(): pass

            asignaciones = data.get('asignaciones')
            if isinstance(asignaciones, list):
                if len(asignaciones) == 0:
                    cur.execute("SELECT idusuariorol FROM tbl_usuariorol WHERE idusuario = %s", (dni,))
                    ids_quitar = [r['idusuariorol'] for r in cur.fetchall()]
                    _borrar_notificaciones_por_usuariorol(cur, ids_quitar)
                    cur.execute("DELETE FROM tbl_usuariorol WHERE idusuario = %s", (dni,))
                else:
                    kept_ids = []
                    for asig in asignaciones:
                        iur = asig.get('idusuariorol')
                        if iur is not None and str(iur).strip():
                            try: kept_ids.append(int(iur))
                            except (TypeError, ValueError): pass
                    if kept_ids:
                        ph = ",".join(["%s"] * len(kept_ids))
                        cur.execute(f"SELECT idusuariorol FROM tbl_usuariorol WHERE idusuario = %s AND idusuariorol NOT IN ({ph})", (dni, *kept_ids))
                        ids_quitar = [r['idusuariorol'] for r in cur.fetchall()]
                        _borrar_notificaciones_por_usuariorol(cur, ids_quitar)
                        cur.execute(f"DELETE FROM tbl_usuariorol WHERE idusuario = %s AND idusuariorol NOT IN ({ph})", (dni, *kept_ids))
                    else:
                        cur.execute("SELECT idusuariorol FROM tbl_usuariorol WHERE idusuario = %s", (dni,))
                        ids_quitar = [r['idusuariorol'] for r in cur.fetchall()]
                        _borrar_notificaciones_por_usuariorol(cur, ids_quitar)
                        cur.execute("DELETE FROM tbl_usuariorol WHERE idusuario = %s", (dni,))

                    for asig in asignaciones:
                        proyecto_id  = asig.get('proyecto_id')
                        rol_id       = asig.get('rol_id')
                        area_id      = asig.get('area_id')
                        cargo        = asig.get('cargo', '').strip() or None
                        idusuariorol = asig.get('idusuariorol')
                        if not proyecto_id or not rol_id: continue
                        if idusuariorol:
                            cur.execute("""
                                UPDATE tbl_usuariorol
                                SET idproyecto=%s, idroles=%s, idarea=%s, cargo=%s
                                WHERE idusuariorol=%s AND idusuario=%s
                            """, (proyecto_id, rol_id, area_id, cargo, idusuariorol, dni))
                        else:
                            cur.execute("""
                                INSERT INTO tbl_usuariorol (idusuario, idproyecto, idroles, idarea, cargo)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (dni, proyecto_id, rol_id, area_id, cargo))

            mysql.connection.commit()
        except Exception as e:
            mysql.connection.rollback()
            import traceback; traceback.print_exc()
            raise
        finally:
            cur.close()

        return jsonify({'success': True, 'message': 'Usuario actualizado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/usuarios/eliminar/<dni>', methods=['POST'])
@admin_required
def usuarios_eliminar(dni):
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tbl_usuario SET activo = 0 WHERE idusuario = %s", (dni,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Usuario desactivado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/usuarios/eliminar-fisico/<dni>', methods=['POST'])
@admin_required
def usuarios_eliminar_fisico(dni):
    try:
        cur = mysql.connection.cursor()
        
        # 1. Eliminar notificaciones ligadas a los roles del usuario
        cur.execute("SELECT idusuariorol FROM tbl_usuariorol WHERE idusuario = %s", (dni,))
        roles = cur.fetchall()
        ids_quitar = [r['idusuariorol'] for r in roles]
        _borrar_notificaciones_por_usuariorol(cur, ids_quitar)
        
        # 2. Eliminar la asignación de roles
        cur.execute("DELETE FROM tbl_usuariorol WHERE idusuario = %s", (dni,))
        
        # 3. Eliminar físicamente el usuario de la DB
        cur.execute("DELETE FROM tbl_usuario WHERE idusuario = %s", (dni,))
        
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'message': 'Usuario eliminado de manera permanente correctamente'})
    except Exception as e:
        mysql.connection.rollback()
        error_msg = str(e)
        if '1451' in error_msg:
            mensaje = "No se puede eliminar permanentemente este usuario porque ya ha generado registros en el sistema (imágenes, inspecciones, etc.). Por favor, utilice la opción de 'Desactivar' para conservar el historial."
            return jsonify({'success': False, 'error': mensaje}), 400
        return jsonify({'success': False, 'error': error_msg}), 500
