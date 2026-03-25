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
                   GROUP_CONCAT(r.nombrerol ORDER BY r.nombrerol SEPARATOR ', ') AS roles,
                   GROUP_CONCAT(r.idroles ORDER BY r.nombrerol SEPARATOR ',') AS roles_ids,
                   MAX(ur.idarea) AS idarea,
                   MAX(ur.cargo) AS cargo
            FROM tbl_usuario u
            LEFT JOIN tbl_usuariorol ur ON ur.idusuario = u.idusuario
            LEFT JOIN tbl_roles r ON r.idroles = ur.idroles
            GROUP BY u.idusuario, u.nombrecompleto, u.correo, u.activo
            ORDER BY u.nombrecompleto
        """)
        usuarios = cur.fetchall()
        cur.execute("SELECT idroles, nombrerol FROM tbl_roles ORDER BY nombrerol")
        roles = cur.fetchall()
        cur.execute("SELECT DISTINCT idarea, nombre FROM tbl_area ORDER BY nombre")
        areas = cur.fetchall()
        cur.close()
        return render_template('configuracion/usuarios.html',
                               usuarios=usuarios, roles=roles, areas=areas,
                               notif_count=get_notif_count())
    except Exception as e:
        import traceback
        return f"<pre>Error: {str(e)}\n{traceback.format_exc()}</pre>", 500


@admin_bp.route('/configuracion/usuarios/crear', methods=['POST'])
@admin_required
@modulo_required('CONFIGURACION')
def usuarios_crear():
    try:
        dni      = request.form.get('dni', '').strip()
        nombre   = request.form.get('nombre', '').strip()
        correo   = request.form.get('correo', '').strip() or None
        rol      = request.form.get('rol', '').strip()
        modulos  = request.form.getlist('modulos')
        idarea   = request.form.get('idarea', '').strip() or None
        cargo    = request.form.get('cargo', '').strip() or None
        pwd_raw  = request.form.get('password', '').strip()
        password = md5(pwd_raw) if pwd_raw else md5('123456')

        if not dni or not nombre or not rol:
            return jsonify({'success': False, 'error': 'DNI, nombre y rol son requeridos'}), 400

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO tbl_usuario (idusuario, nombrecompleto, correo, contrasena) VALUES (%s,%s,%s,%s)",
            (dni, nombre, correo, password)
        )
        cur.execute(
            "INSERT INTO tbl_usuariorol (idusuario, idroles, idarea, cargo) VALUES (%s,%s,%s,%s)",
            (dni, rol, idarea, cargo)
        )
        for mid in modulos:
            cur.execute(
                "INSERT IGNORE INTO tbl_modulo_permiso (idmodulo, idroles, idarea) VALUES (%s,%s,%s)",
                (mid, rol, idarea or 0)
            )
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/configuracion/usuarios/editar/<uid>', methods=['POST'])
@admin_required
@modulo_required('CONFIGURACION')
def usuarios_editar(uid):
    try:
        nombre = request.form.get('nombre', '').strip()
        correo = request.form.get('correo', '').strip() or None
        rol    = request.form.get('rol', '').strip()
        idarea = request.form.get('idarea', '').strip() or None
        cargo  = request.form.get('cargo', '').strip() or None

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE tbl_usuario SET nombrecompleto=%s, correo=%s WHERE idusuario=%s",
            (nombre, correo, uid)
        )
        cur.execute("DELETE FROM tbl_usuariorol WHERE idusuario=%s", (uid,))
        if rol:
            cur.execute(
                "INSERT INTO tbl_usuariorol (idusuario, idroles, idarea, cargo) VALUES (%s,%s,%s,%s)",
                (uid, rol, idarea, cargo)
            )
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/configuracion/roles/<int:rol_id>/modulos')
@admin_required
@modulo_required('CONFIGURACION')
def modulos_por_rol(rol_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT m.idmodulo, m.codigo, m.nombre, m.icono, m.url, m.orden
            FROM tbl_modulo m
            JOIN tbl_modulo_permiso mp ON mp.idmodulo = m.idmodulo
            WHERE mp.idroles = %s AND m.activo = 1
            ORDER BY m.orden ASC
        """, (rol_id,))
        modulos = cur.fetchall()
        cur.close()
        return jsonify({'success': True, 'modulos': [
            {'idmodulo': m['idmodulo'], 'codigo': m['codigo'],
             'nombre': m['nombre'], 'icono': m['icono'] or 'circle', 'url': m['url']}
            for m in modulos
        ]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/configuracion/roles/<int:rol_id>/modulos/guardar', methods=['POST'])
@admin_required
@modulo_required('CONFIGURACION')
def guardar_modulos_rol(rol_id):
    try:
        data = request.get_json()
        modulos_ids = [int(m) for m in data.get('modulos', [])]
        cur = mysql.connection.cursor()
        cur.execute("SELECT idmodulo FROM tbl_modulo WHERE activo = 1")
        todos = [r['idmodulo'] for r in cur.fetchall()]
        for mid in todos:
            if mid in modulos_ids:
                cur.execute(
                    "INSERT IGNORE INTO tbl_modulo_permiso (idmodulo, idroles, idarea) VALUES (%s,%s,0)",
                    (mid, rol_id)
                )
            else:
                cur.execute(
                    "DELETE FROM tbl_modulo_permiso WHERE idmodulo=%s AND idroles=%s",
                    (mid, rol_id)
                )
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/configuracion/usuarios/toggle/<uid>', methods=['POST'])
@admin_required
@modulo_required('CONFIGURACION')
def usuarios_toggle(uid):
    try:
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tbl_usuario SET activo = NOT activo WHERE idusuario=%s", (uid,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/configuracion/usuarios/eliminar/<uid>', methods=['POST'])
@admin_required
@modulo_required('CONFIGURACION')
def usuarios_eliminar(uid):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM tbl_usuario WHERE idusuario=%s", (uid,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/configuracion/usuarios/password', methods=['POST'])
@admin_required
@modulo_required('CONFIGURACION')
def usuarios_password():
    try:
        uid = request.form.get('usuario_id', '').strip()
        pwd = request.form.get('nueva_password', '').strip()
        if not uid or not pwd:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tbl_usuario SET contrasena=%s WHERE idusuario=%s", (md5(pwd), uid))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ── Notificaciones ────────────────────────────────────────────────────────────

@admin_bp.route('/notificaciones/leer/<nid>', methods=['POST'])
@admin_required
def leer_notificacion(nid):
    cur = mysql.connection.cursor()
    sp_exec(cur, 'sp_leernotificacion', (nid,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})


@admin_bp.route('/notificaciones/todas', methods=['POST'])
@admin_required
def leer_todas():
    cur = mysql.connection.cursor()
    cur.execute("UPDATE tbl_notificacion SET leida=1 WHERE idusuariorol=%s", (session['usuario_rol'],))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})


# ── Gestión de Aguas ──────────────────────────────────────────────────────────

@admin_bp.route('/aguas')
@admin_required
def gestion_aguas():
    return render_template('admin/gestion_aguas.html', notif_count=get_notif_count())


@admin_bp.route('/ana')
@admin_required
def reporte_ana():
    return render_template('admin/reporte_ana.html', notif_count=get_notif_count())


# ── Debug ─────────────────────────────────────────────────────────────────────

@admin_bp.route('/debug/modulos')
@admin_required
def debug_modulos():
    return jsonify({
        'accesos':  session.get('accesos', []),
        'modulos':  session.get('modulos', []),
        'rol':      session.get('rol'),
        'rol_id':   session.get('rol_id'),
        'user_id':  session.get('user_id'),
    })
