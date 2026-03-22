from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from functools import wraps
from extensions import mysql
from utils.helpers import gen_id, save_image, sp_exec, sp_one
import io
import os
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('rol') != 'Administrador':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def modulo_required(codigo):
    """Verifica que el usuario tenga acceso al modulo indicado."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            if codigo not in session.get('accesos', []):
                return render_template('auth/sin_acceso.html'), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def get_notif_count():
    try:
        cur = mysql.connection.cursor()
        rows = sp_exec(cur, 'sp_contarnotificaciones', (session['usuario_rol'],))
        cur.close()
        return rows[0]['total'] if rows else 0
    except:
        return 0

def get_maestros():
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM tbl_areareportante ORDER BY areareportante")
    areas_rep = cur.fetchall()
    
    cur.execute("SELECT * FROM tbl_arearesponsable ORDER BY arearesponsable")
    areas_res = cur.fetchall()
    
    cur.execute("SELECT * FROM tbl_ubicacion ORDER BY ubicacion")
    ubicaciones = cur.fetchall()
    
    cur.execute("SELECT * FROM tbl_riesgo")
    riesgos = cur.fetchall()
    
    cur.execute("SELECT * FROM tbl_descripciontipo ORDER BY descripciontipo")
    tipos = cur.fetchall()
    
    cur.execute("SELECT * FROM tbl_estado ORDER BY orden")
    estados = cur.fetchall()
    
    cur.close()
    return areas_rep, areas_res, ubicaciones, riesgos, tipos, estados

@admin_bp.route('/dashboard')
@admin_required
@modulo_required('DASHBOARD')
def dashboard():
    cur = mysql.connection.cursor()
    stats = sp_one(cur, 'sp_dashboardstats')
    cur.close()
    
    cur = mysql.connection.cursor()
    notifs = sp_exec(cur, 'sp_notificaciones', (session['usuario_rol'],))
    cur.close()
    
    # Obtener registros pendientes para la tabla del dashboard
    cur = mysql.connection.cursor()
    todos = sp_exec(cur, 'sp_listarregistros', (None,))
    cur.close()
    
    registros_pendientes = [r for r in todos if r.get('estado') == 'Pendiente']
    total_pendientes = len(registros_pendientes)
    
    return render_template('desvios_ambientales/dashboard.html',
        stats=stats or {'total':0,'culminados':0,'en_proceso':0,'pendientes':0},
        notifs=notifs,
        notif_count=get_notif_count(),
        registros=registros_pendientes,
        total=total_pendientes,
        page=1,
        total_pages=1,
        per_page=total_pendientes or 10,
        estado_filter='Pendiente',
        personal_filter='')

@admin_bp.route('/registrar')
@admin_required
@modulo_required('DESVIOS')
def registrar():
    estado_filter = request.args.get('estado','')
    personal_filter = request.args.get('personal','')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Obtener TODOS los registros sin filtro para extraer estados únicos
    cur = mysql.connection.cursor()
    todos_registros = sp_exec(cur, 'sp_listarregistros', (None,))
    cur.close()
    
    # Obtener estados únicos de TODOS los registros
    estados_unicos = sorted(list(set([r.get('estado', '') for r in todos_registros if r.get('estado')])))
    
    # Ahora obtener registros con filtro si aplica
    cur = mysql.connection.cursor()
    registros = sp_exec(cur, 'sp_listarregistros', (estado_filter or None,))
    cur.close()
    
    # Filtrar por personal responsable si se especifica
    if personal_filter:
        registros = [r for r in registros if r.get('personalresponsable', '').lower() == personal_filter.lower()]
    
    # Definir orden de prioridad de estados
    orden_estados = {
        'Pendiente': 1,
        'En Proceso': 2,
        'Enviado': 3,
        'En Revisión': 4,
        'Culminado': 5,
        'Rechazado': 6,
        'Cerrado': 7
    }
    
    # Ordenar registros por prioridad de estado
    registros_ordenados = sorted(
        registros, 
        key=lambda x: orden_estados.get(x.get('estado', ''), 999)
    )
    
    # Calcular paginación
    total = len(registros_ordenados)
    total_pages = (total + per_page - 1) // per_page  # Redondeo hacia arriba
    
    # Validar página
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Obtener registros de la página actual
    start = (page - 1) * per_page
    end = start + per_page
    registros_pagina = registros_ordenados[start:end]
    
    areas_rep, areas_res, ubicaciones, riesgos, tipos, estados = get_maestros()
    
    return render_template('desvios_ambientales/desvios.html',
        registros=registros_pagina,
        areas_rep=areas_rep, areas_res=areas_res,
        ubicaciones=ubicaciones, riesgos=riesgos, tipos=tipos, estados=estados,
        estado_filter=estado_filter,
        personal_filter=personal_filter,
        notif_count=get_notif_count(),
        page=page,
        total_pages=total_pages,
        total=total,
        per_page=per_page,
        estados_unicos=estados_unicos)

@admin_bp.route('/estadisticas')
@admin_required
@modulo_required('ESTADISTICAS')
def estadisticas():
    return render_template('desvios_ambientales/estadisticas.html', notif_count=get_notif_count())

@admin_bp.route('/estadisticas/areas')
@admin_required
@modulo_required('ESTADISTICAS')
def estadisticas_areas():
    fecha_ini = request.args.get('fecha_ini') or None
    fecha_fin = request.args.get('fecha_fin') or None
    cur = mysql.connection.cursor()
    stats = sp_exec(cur, 'sp_estadisticasareas', (fecha_ini, fecha_fin))
    cur.close()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = [{'area_responsable': r.get('AreaReportante') or r.get('areareportante',''),
                 'total':     r.get('total', 0),
                 'culminado': r.get('culminado', 0),
                 'pendiente': r.get('pendiente', 0),
                 'proceso':   r.get('proceso', 0)} for r in stats]
        return jsonify(data)
    return redirect(url_for('admin.estadisticas'))

@admin_bp.route('/estadisticas/ccta')
@admin_required
@modulo_required('ESTADISTICAS')
def estadisticas_ccta():
    fecha_ini = request.args.get('fecha_ini') or None
    fecha_fin = request.args.get('fecha_fin') or None
    cur = mysql.connection.cursor()
    stats = sp_exec(cur, 'sp_estadisticasccta', (fecha_ini, fecha_fin))
    cur.close()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = [{'ccta_responsable': str(r.get('ccta_responsable') or r.get('CctaResponsable') or 'Sin asignar'),
                 'total':     r.get('total', 0),
                 'culminado': r.get('culminado', 0),
                 'pendiente': r.get('pendiente', 0),
                 'proceso':   r.get('proceso', 0)} for r in stats]
        return jsonify(data)
    return redirect(url_for('admin.estadisticas'))

@admin_bp.route('/estadisticas/tipos')
@admin_required
@modulo_required('ESTADISTICAS')
def estadisticas_tipos():
    fecha_ini = request.args.get('fecha_ini') or None
    fecha_fin = request.args.get('fecha_fin') or None
    cur = mysql.connection.cursor()
    stats = sp_exec(cur, 'sp_estadisticas_tipos_pendientes', (fecha_ini, fecha_fin))
    cur.close()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = [{'tipo_descripcion':   r.get('DescripcionTipo') or r.get('descripciontipo',''),
                 'cantidad_pendiente': r.get('pendiente') or r.get('total', 0)} for r in stats]
        return jsonify(data)
    return redirect(url_for('admin.estadisticas'))

@admin_bp.route('/configuracion/dashboard')
@admin_required
@modulo_required('CONFIG_DASH')
def configuracion_dashboard():
    return render_template('configuracion/dashboard.html', notif_count=get_notif_count())

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
        traceback.print_exc()
        return f"<pre>Error: {str(e)}\n{traceback.format_exc()}</pre>", 500


@admin_bp.route('/configuracion/usuarios/crear', methods=['POST'])
@admin_required
@modulo_required('CONFIGURACION')
def usuarios_crear():
    from utils.helpers import md5
    try:
        dni     = request.form.get('dni','').strip()
        nombre  = request.form.get('nombre','').strip()
        correo  = request.form.get('correo','').strip() or None
        rol     = request.form.get('rol','').strip()          # un solo rol
        modulos = request.form.getlist('modulos')             # ids de módulos seleccionados
        idarea  = request.form.get('idarea','').strip() or None
        cargo   = request.form.get('cargo','').strip() or None
        pwd_raw = request.form.get('password','').strip()
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
        # Obtener el idusuariorol recién creado
        cur.execute("SELECT LAST_INSERT_ID() AS id")
        ur_id = cur.fetchone()['id']

        # Guardar permisos de módulos personalizados para este usuario
        # Usamos tbl_modulo_permiso con idusuariorol para permisos individuales
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
        nombre  = request.form.get('nombre','').strip()
        correo  = request.form.get('correo','').strip() or None
        rol     = request.form.get('rol','').strip()
        modulos = request.form.getlist('modulos')
        idarea  = request.form.get('idarea','').strip() or None
        cargo   = request.form.get('cargo','').strip() or None

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
    """Devuelve los módulos asignados a un rol para cargarlos dinámicamente."""
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
             'nombre': m['nombre'], 'icono': m['icono'] or 'circle',
             'url': m['url']}
            for m in modulos
        ]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@admin_bp.route('/configuracion/roles/<int:rol_id>/modulos/guardar', methods=['POST'])
@admin_required
@modulo_required('CONFIGURACION')
def guardar_modulos_rol(rol_id):
    """Actualiza los módulos permitidos para un rol en tbl_modulo_permiso."""
    try:
        data = request.get_json()
        modulos_ids = [int(m) for m in data.get('modulos', [])]

        cur = mysql.connection.cursor()
        # Obtener todos los módulos activos para saber cuáles quitar
        cur.execute("SELECT idmodulo FROM tbl_modulo WHERE activo = 1")
        todos = [r['idmodulo'] for r in cur.fetchall()]

        for mid in todos:
            if mid in modulos_ids:
                # Asegurar que existe el permiso
                cur.execute("""
                    INSERT IGNORE INTO tbl_modulo_permiso (idmodulo, idroles, idarea)
                    VALUES (%s, %s, 0)
                """, (mid, rol_id))
            else:
                # Quitar el permiso
                cur.execute("""
                    DELETE FROM tbl_modulo_permiso
                    WHERE idmodulo = %s AND idroles = %s
                """, (mid, rol_id))

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
    from utils.helpers import md5
    try:
        uid  = request.form.get('usuario_id','').strip()
        pwd  = request.form.get('nueva_password','').strip()
        if not uid or not pwd:
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        cur = mysql.connection.cursor()
        cur.execute("UPDATE tbl_usuario SET contrasena=%s WHERE idusuario=%s", (md5(pwd), uid))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Mantener la ruta /desvios para redireccionar a /registrar
@admin_bp.route('/desvios')
@admin_required
def desvios():
    return redirect(url_for('admin.registrar', **request.args))

@admin_bp.route('/desvios/crear', methods=['POST'])
@admin_required
@modulo_required('DESVIOS')
def crear_registro():
    try:
        cur = mysql.connection.cursor()
        corr = sp_one(cur, 'sp_siguientecorrelativo')
        cur.close()
        
        codigo = corr['correlativo'] if corr else '001-01'

        cur = mysql.connection.cursor()
        result = sp_one(cur, 'sp_crearregistro', (
            codigo,
            request.form.get('fecha_inicio') or datetime.now().strftime('%Y-%m-%d'),
            request.form.get('fecha_ejecucion') or None,
            request.form['descripcion'],
            request.form.get('accion',''),
            int(request.form['area_reportante']), int(request.form['area_responsable']),
            int(request.form['ubicacion']), int(request.form['riesgo']), int(request.form['tipo']),
            1, session['usuario_rol'],
            request.form.get('personal_responsable',''),
            int(request.form['ccta_responsable']) if request.form.get('ccta_responsable') else 0,
            request.form.get('dni_responsable','').strip()
        ))
        mysql.connection.commit()
        cur.close()
        rid = result['idregistro'] if result else None

        for f in request.files.getlist('evidencias')[:5]:
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'evidencias')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (rid, session['usuario_rol'], 1, 1, ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()

        for f in request.files.getlist('levantamientos')[:5]:
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'levantamientos')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (rid, session['usuario_rol'], 2, 1, ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()

        cur = mysql.connection.cursor()
        cur.execute("SELECT ur.idusuariorol FROM tbl_usuariorol ur JOIN tbl_roles r ON r.idroles=ur.idroles WHERE r.nombrerol IN ('Supervisor','Trabajador')")
        sups = cur.fetchall()
        cur.close()
        
        for s in sups:
            cur = mysql.connection.cursor()
            sp_exec(cur, 'sp_crearnotificacion', (s['idusuariorol'], f'Nuevo reporte {codigo} creado', 'info', rid))
            mysql.connection.commit()
            cur.close()

        # Verificar si es petición AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Reporte creado exitosamente',
                'registro_id': rid,
                'codigo': codigo
            })
        
        flash('Reporte creado exitosamente', 'success')
    except Exception as e:
        import traceback
        traceback.print_exc()
        msg = f'Error al crear reporte: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': msg}), 400
        flash(msg, 'error')
    return redirect(url_for('admin.registrar'))

@admin_bp.route('/desvios/editar/<rid>', methods=['POST'])
@admin_required
@modulo_required('DESVIOS')
def editar_registro(rid):
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_actualizarregistro', (
            rid,
            request.form.get('fecha_inicio') or datetime.now().strftime('%Y-%m-%d'),
            request.form.get('fecha_ejecucion') or None,
            request.form['descripcion'], request.form.get('accion',''),
            int(request.form['area_reportante']), int(request.form['area_responsable']),
            int(request.form['ubicacion']), int(request.form['riesgo']), int(request.form['tipo']),
            int(request.form['estado']),
            request.form.get('personal_responsable',''),
            int(request.form['ccta_responsable']) if request.form.get('ccta_responsable','').strip() not in ('', '0', 'None') else 0,
            request.form.get('dni_responsable','').strip()
        ))
        mysql.connection.commit()
        cur.close()
        
        # Manejar eliminación de imágenes
        imagenes_eliminar = request.form.get('imagenes_eliminar', '')
        if imagenes_eliminar:
            ids_eliminar = [id.strip() for id in imagenes_eliminar.split(',') if id.strip()]
            for imagen_id in ids_eliminar:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_eliminarimagen', (imagen_id,))
                mysql.connection.commit()
                cur.close()
        
        # Agregar nuevas evidencias
        for f in request.files.getlist('nuevas_evidencias')[:5]:
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'evidencias')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (rid, session['usuario_rol'], 1, 1, ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()
        
        # Agregar nuevos levantamientos
        for f in request.files.getlist('nuevos_levantamientos')[:5]:
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'levantamientos')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (rid, session['usuario_rol'], 2, 1, ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()
        
        flash('Reporte actualizado', 'success')
        
        # Soporte AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Reporte actualizado exitosamente'
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Soporte AJAX para errores
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': f'Error: {str(e)}',
                'traceback': traceback.format_exc()
            }), 400
            
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('admin.registrar'))


@admin_bp.route('/desvios/eliminar/<rid>', methods=['POST'])
@admin_required
@modulo_required('DESVIOS')
def eliminar_registro(rid):
    try:
        cur = mysql.connection.cursor()
        # Obtener rutas de imágenes antes de borrar
        cur.execute("SELECT rutaimagen FROM tbl_imagenregistro WHERE idregistro=%s", (rid,))
        imagenes = cur.fetchall()

        # Borrar en orden por FK
        cur.execute("DELETE FROM tbl_historialaprobacion WHERE idregistro=%s", (rid,))
        cur.execute("DELETE FROM tbl_notificacion WHERE idregistro=%s", (rid,))
        cur.execute("DELETE FROM tbl_registro WHERE idregistro=%s", (rid,))
        mysql.connection.commit()
        cur.close()

        # Borrar archivos físicos
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        for img in imagenes:
            ruta = img.get('rutaimagen', '')  # ej: "uploads/evidencias/abc.jpg"
            if ruta:
                filepath = os.path.normpath(os.path.join(base_dir, 'static', ruta))
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                except:
                    pass

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        flash('Registro eliminado', 'success')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
        flash(f'Error al eliminar: {str(e)}', 'error')
    return redirect(url_for('admin.registrar'))


@admin_bp.route('/desvios/detalle/<rid>')
@admin_required
@modulo_required('DESVIOS')
def detalle_registro(rid):
    cur = mysql.connection.cursor()
    registro = sp_one(cur, 'sp_detalleregistro', (rid,))
    cur.close()
    
    cur = mysql.connection.cursor()
    imagenes = sp_exec(cur, 'sp_imagenesregistro', (rid,))
    cur.close()

    def serialize(obj):
        if obj is None: return {}
        out = {}
        for k, v in obj.items():
            key = k.lower()  # normalizar a minúsculas para el JS
            if hasattr(v, 'strftime'):
                out[key] = v.strftime('%Y-%m-%d')
            else:
                out[key] = v if v is not None else ''
        return out

    # Filtrar solo imágenes que NO estén rechazadas (EIM003)
    imgs_serial = []
    for i in imagenes:
        if i.get('idEstadoImagen') != 3:
            imgs_serial.append(serialize(i))

    # Separar por tipo (claves ya en minúsculas tras serialize)
    evidencias = []
    levantamientos = []
    for img in imgs_serial:
        if img.get('idtipoimagen') == 1:
            evidencias.append(img)
        elif img.get('idtipoimagen') == 2:
            levantamientos.append(img)

    result = {
        'registro': serialize(registro),
        'evidencias': evidencias,
        'levantamientos': levantamientos
    }
    
    return jsonify(result)

@admin_bp.route('/desvios/validar/<rid>', methods=['POST'])
@admin_required
@modulo_required('DESVIOS')
def validar_levantamiento(rid):
    try:
        decision = request.form.get('decision')
        comentario = request.form.get('comentario','')
        
        if decision == 'APROBADA':
            # APROBAR: Solo las imágenes que quedaron en el modal
            imagenes_ids = request.form.get('imagenes_ids','')
            if not imagenes_ids:
                flash('No se recibieron imágenes para aprobar', 'error')
                return redirect(url_for('admin.registrar'))
            
            ids_list = [id.strip() for id in imagenes_ids.split(',') if id.strip()]
            
            # Primero: ELIMINAR físicamente las imágenes que fueron quitadas con X
            imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar','')
            if imagenes_ids_rechazar:
                ids_rechazar_list = [id.strip() for id in imagenes_ids_rechazar.split(',') if id.strip()]
                ids_eliminar = [id for id in ids_rechazar_list if id not in ids_list]
                
                for imagen_id in ids_eliminar:
                    cur = mysql.connection.cursor()
                    # Eliminar físicamente la imagen
                    sp_exec(cur, 'sp_eliminarimagen', (imagen_id,))
                    mysql.connection.commit()
                    cur.close()
            
            # Segundo: Aprobar las imágenes seleccionadas (esto cambia estado a COMPLETADO)
            for imagen_id in ids_list:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_validarimagen', (imagen_id, rid, session['usuario_rol'], 'APROBADA', comentario))
                mysql.connection.commit()
                cur.close()
            
            cantidad = len(ids_list)
            flash(f'{cantidad} imagen(es) aprobada(s) correctamente', 'success')
            
        else:
            # RECHAZAR: TODAS las imágenes originales
            imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar','')
            if not imagenes_ids_rechazar:
                flash('No se recibieron imágenes para rechazar', 'error')
                return redirect(url_for('admin.registrar'))
            
            ids_list = [id.strip() for id in imagenes_ids_rechazar.split(',') if id.strip()]
            
            # Rechazar todas las imágenes originales (esto cambia estado a PENDIENTE)
            for imagen_id in ids_list:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_validarimagen', (imagen_id, rid, session['usuario_rol'], 'RECHAZADA', comentario))
                mysql.connection.commit()
                cur.close()
            
            cantidad = len(ids_list)
            flash(f'{cantidad} imagen(es) rechazada(s). El supervisor debe volver a subir imágenes', 'warning')
        
        # Obtener usuarios para notificar
        imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar','')
        if imagenes_ids_rechazar:
            ids_notif = [id.strip() for id in imagenes_ids_rechazar.split(',') if id.strip()]
            cur = mysql.connection.cursor()
            cur.execute("SELECT DISTINCT idusuariorol FROM tbl_imagenregistro WHERE idimagen IN (%s)" % ','.join(['%s']*len(ids_notif)), ids_notif)
            usuarios = cur.fetchall()
            cur.close()
            
            # Enviar notificación
            for usuario in usuarios:
                msg = f'Tu conjunto de imágenes fue {"APROBADO" if decision=="APROBADA" else "RECHAZADO"}'
                if comentario: 
                    msg += f': {comentario}'
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_crearnotificacion', (usuario['idusuariorol'], msg,
                        'success' if decision=='APROBADA' else 'warning', rid))
                mysql.connection.commit()
                cur.close()
        
        # Soporte AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': f'Imágenes {"aprobadas" if decision=="APROBADA" else "rechazadas"} exitosamente'
            })
        
    except Exception as e:
        # Soporte AJAX para errores
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': f'Error: {str(e)}'
            }), 400
            
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('admin.registrar'))

@admin_bp.route('/exportar')
@admin_required
@modulo_required('DESVIOS')
def exportar_excel():
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        from openpyxl.drawing.image import Image as XLImage
        from PIL import Image as PILImage
        import os
        import tempfile
        
        # Obtener registros
        cur  = mysql.connection.cursor()
        rows = sp_exec(cur, 'sp_exportarregistros')
        cur.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Desvíos Ambientales"
        hfill = PatternFill("solid", fgColor="1a7a3c")
        hfont = Font(bold=True, color="FFFFFF", size=11)
        thin  = Border(left=Side(style='thin'),right=Side(style='thin'),
                       top=Side(style='thin'),bottom=Side(style='thin'))
        
        # Headers
        headers = ['Código','Fecha','Fecha Ejecución','Área Reportante','Ubicación',
                   'Descripción','Tipo','Riesgo','Estado','Acción',
                   'Área Responsable','Personal Responsable','Fecha Creación',
                   'Evidencias','Levantamientos']
        col_w   = [12,14,16,20,30,40,30,12,14,40,22,22,18,25,25]
        
        for i,(h,w) in enumerate(zip(headers,col_w),1):
            c = ws.cell(row=1,column=i,value=h)
            c.fill=hfill; c.font=hfont; c.border=thin
            c.alignment=Alignment(horizontal='center',vertical='center')
            ws.column_dimensions[get_column_letter(i)].width=w
        
        alt = PatternFill("solid", fgColor="f0f9f4")
        current_row = 2
        
        # Lista para guardar archivos temporales y limpiarlos al final
        temp_files = []
        
        for row in rows:
            # Obtener imágenes del registro
            cur = mysql.connection.cursor()
            imagenes = sp_exec(cur, 'sp_imagenesregistro', (row.get('IdRegistro',''),))
            cur.close()
            
            # Filtrar imágenes no rechazadas
            evidencias = []
            levantamientos = []
            for img in imagenes:
                if img.get('idEstadoImagen') != 3:  # Excluir rechazadas
                    if img.get('idTipoImagen') == 1:
                        evidencias.append(img.get('RutaImagen',''))
                    elif img.get('idTipoImagen') == 2:
                        levantamientos.append(img.get('RutaImagen',''))
            
            # Calcular cuántas filas necesitamos
            max_images = max(len(evidencias), len(levantamientos), 1)
            
            # Datos del registro
            vals=[row.get('Codigo',''),row.get('Fecha',''),row.get('FechaEjecucion',''),
                  row.get('AreaReportante',''),row.get('Ubicacion',''),row.get('Descripcion',''),
                  row.get('DescripcionTipo',''),row.get('Riesgo',''),row.get('Estado',''),
                  row.get('Accion',''),row.get('AreaResponsable',''),
                  row.get('PersonalResponsable',''),row.get('FechaCreacion','')]
            
            # Escribir datos del registro en la primera fila
            for ci,v in enumerate(vals,1):
                c=ws.cell(row=current_row,column=ci,value=str(v) if v else '')
                c.border=thin
                c.alignment=Alignment(vertical='center',wrap_text=True)
                if current_row%2==0: c.fill=alt
                
                # Si hay múltiples imágenes, hacer merge de celdas verticalmente
                if max_images > 1:
                    ws.merge_cells(start_row=current_row, start_column=ci, 
                                  end_row=current_row+max_images-1, end_column=ci)
            
            # Insertar imágenes en filas separadas
            for img_idx in range(max_images):
                img_row = current_row + img_idx
                
                # Ajustar altura de fila para imágenes
                ws.row_dimensions[img_row].height = 100
                
                # Insertar evidencia si existe
                if img_idx < len(evidencias):
                    img_path = evidencias[img_idx]
                    
                    # Probar diferentes rutas posibles
                    possible_paths = [
                        img_path,
                        os.path.join('ecosupervisor', img_path),
                        os.path.join('static', img_path.replace('static/', '')),
                        os.path.join('ecosupervisor', 'static', img_path.replace('static/', ''))
                    ]
                    
                    full_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            full_path = path
                            break
                    
                    if full_path:
                        try:
                            # Crear thumbnail
                            pil_img = PILImage.open(full_path)
                            pil_img.thumbnail((80, 80), PILImage.Resampling.LANCZOS)
                            
                            # Crear archivo temporal con nombre único
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                            temp_path = temp_file.name
                            temp_file.close()
                            temp_files.append(temp_path)
                            
                            # Guardar thumbnail
                            pil_img.save(temp_path, 'PNG')
                            
                            # Insertar en Excel
                            xl_img = XLImage(temp_path)
                            cell_ref = f'{get_column_letter(14)}{img_row}'
                            ws.add_image(xl_img, cell_ref)
                            
                        except Exception as e:
                            ws.cell(row=img_row, column=14, value=f'Error: {str(e)[:30]}')
                    else:
                        ws.cell(row=img_row, column=14, value='No encontrada')
                
                # Insertar levantamiento si existe
                if img_idx < len(levantamientos):
                    img_path = levantamientos[img_idx]
                    
                    # Probar diferentes rutas posibles
                    possible_paths = [
                        img_path,
                        os.path.join('ecosupervisor', img_path),
                        os.path.join('static', img_path.replace('static/', '')),
                        os.path.join('ecosupervisor', 'static', img_path.replace('static/', ''))
                    ]
                    
                    full_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            full_path = path
                            break
                    
                    if full_path:
                        try:
                            # Crear thumbnail
                            pil_img = PILImage.open(full_path)
                            pil_img.thumbnail((80, 80), PILImage.Resampling.LANCZOS)
                            
                            # Crear archivo temporal con nombre único
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                            temp_path = temp_file.name
                            temp_file.close()
                            temp_files.append(temp_path)
                            
                            # Guardar thumbnail
                            pil_img.save(temp_path, 'PNG')
                            
                            # Insertar en Excel
                            xl_img = XLImage(temp_path)
                            cell_ref = f'{get_column_letter(15)}{img_row}'
                            ws.add_image(xl_img, cell_ref)
                            
                        except Exception as e:
                            ws.cell(row=img_row, column=15, value=f'Error: {str(e)[:30]}')
                    else:
                        ws.cell(row=img_row, column=15, value='No encontrada')
                
                # Agregar bordes a las celdas de imágenes
                for col in [14, 15]:
                    c = ws.cell(row=img_row, column=col)
                    c.border = thin
                    if current_row%2==0: c.fill=alt
            
            # Avanzar a la siguiente fila después de todas las imágenes
            current_row += max_images
        
        # Guardar el Excel
        out=io.BytesIO()
        wb.save(out)
        out.seek(0)
        
        # Limpiar archivos temporales
        for temp_path in temp_files:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
        
        fname=f"desvios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(out,download_name=fname,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True)
    except Exception as e:
        flash(f'Error al exportar: {str(e)}','error')
        return redirect(url_for('admin.registrar'))

@admin_bp.route('/debug/modulos')
@admin_required
def debug_modulos():
    """Endpoint temporal para ver qué módulos devuelve la BD para el rol actual."""
    from routes.auth import _query_modulos, cargar_modulos
    rol_id = session.get('rol_id')
    rows = _query_modulos(rol_id)
    modulos_sidebar = cargar_modulos(rol_id)
    return jsonify({
        'rol_id': rol_id,
        'rol': session.get('rol'),
        'raw_desde_bd': [{'codigo': r['codigo'], 'orden': r['orden'], 'url': r['url']} for r in rows],
        'sidebar_final': [{'codigo': m['codigo'], 'orden': m['orden'], 'hijos': [h['codigo'] for h in m['hijos']]} for m in modulos_sidebar]
    })

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




