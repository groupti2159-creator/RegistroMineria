from flask import render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from extensions import mysql
from utils.helpers import save_image, sp_exec, sp_one, get_notif_count, modulo_required, delete_image_file
from utils.workflow import EstadoWorkflow, EventosWorkflow
from routes.core.supervisor import supervisor_bp


def sup_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        # Permitir cualquier usuario logueado (la restricción real la hace @modulo_required)
        return f(*args, **kwargs)
    return decorated


@supervisor_bp.route('/desvios')
@sup_required
@modulo_required(('DESVIOS', 'MIS_REPORTES'))
def desvios():
    estado_filter = request.args.get('estado', '')
    page     = request.args.get('page', 1, type=int)
    per_page = 10

    # Obtener proyecto del usuario
    proyecto_id = session.get('proyecto_id', 1)

    cur = mysql.connection.cursor()
    todos_registros = sp_exec(cur, 'sp_listarregistrossupervisor', (None, proyecto_id))
    cur.close()
    estados_unicos = sorted(list(set([r.get('estado', '') for r in todos_registros if r.get('estado')])))

    cur = mysql.connection.cursor()
    registros = sp_exec(cur, 'sp_listarregistrossupervisor', (estado_filter or None, proyecto_id))
    cur.close()

    orden_estados = {
        'Pendiente': 1, 'Atrasado': 2, 'Asignado': 3,
        'En Proceso': 4, 'Enviado': 5, 'En Revision': 6,
        'Culminado': 7, 'Rechazado': 8, 'Cerrado': 9
    }
    registros_ordenados = sorted(registros, key=lambda x: orden_estados.get(x.get('estado', ''), 999))

    total       = len(registros_ordenados)
    total_pages = (total + per_page - 1) // per_page
    page        = max(1, min(page, total_pages) if total_pages > 0 else 1)
    start       = (page - 1) * per_page

    cur = mysql.connection.cursor()
    notifs = sp_exec(cur, 'sp_notificaciones', (session['usuario_rol'],))
    cur.close()

    # Obtener rol del usuario
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.nombrerol 
        FROM tbl_usuariorol ur
        JOIN tbl_roles r ON ur.idroles = r.idroles
        WHERE ur.idusuario = %s
        LIMIT 1
    """, (session['user_id'],))
    
    resultado = cur.fetchone()
    cur.close()
    
    usuario_rol = resultado['nombrerol'] if resultado else None

    return render_template('desvios_ambientales/supervisor_desvios.html',
        registros=registros_ordenados[start:start + per_page], notifs=notifs,
        estado_filter=estado_filter, notif_count=get_notif_count(),
        page=page, total_pages=total_pages, total=total, per_page=per_page,
        estados_unicos=estados_unicos,
        usuario_rol=usuario_rol)


@supervisor_bp.route('/desvios/detalle/<rid>')
@sup_required
@modulo_required(('DESVIOS', 'MIS_REPORTES'))
def detalle_registro(rid):
    cur = mysql.connection.cursor()
    registro = sp_one(cur, 'sp_detalleregistro', (rid,))
    cur.close()
    cur = mysql.connection.cursor()
    imagenes = sp_exec(cur, 'sp_imagenesregistro', (rid,))
    cur.close()

    def serialize(obj):
        if obj is None: return {}
        return {k.lower(): (v.strftime('%Y-%m-%d ') if hasattr(v, 'strftime') else (v if v is not None else ''))
                for k, v in obj.items()}

    imgs_serial    = [serialize(i) for i in imagenes if i.get('idEstadoImagen') != 3]
    return jsonify({
        'registro':       serialize(registro),
        'evidencias':     [i for i in imgs_serial if i.get('idtipoimagen') == 1],
        'levantamientos': [i for i in imgs_serial if i.get('idtipoimagen') == 2]
    })


@supervisor_bp.route('/desvios/subir/<rid>', methods=['POST'])
@sup_required
@modulo_required(('DESVIOS', 'MIS_REPORTES'))
def subir_levantamiento(rid):
    # Verificar que el usuario es Supervisor
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.nombrerol 
        FROM tbl_usuariorol ur
        JOIN tbl_roles r ON ur.idroles = r.idroles
        WHERE ur.idusuario = %s
        LIMIT 1
    """, (session['user_id'],))
    
    resultado = cur.fetchone()
    cur.close()
    
    rol_usuario = resultado['nombrerol'] if resultado else None
    
    if rol_usuario != 'Supervisor':
        flash('Solo los Supervisores pueden subir levantamientos de observaciones', 'error')
        return redirect(url_for('supervisor.desvios'))
    try:
        # Obtener detalles de la acción del formulario
        detalles_accion = request.form.get('detalles_accion', '').strip()
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) AS cnt FROM tbl_imagenregistro WHERE idregistro=%s AND idtipoimagen=2 AND idestadoimagen != 3", (rid,))
        existing = (cur.fetchone() or {}).get('cnt', 0)
        cur.close()

        saved = 0
        for f in request.files.getlist('imagenes'):
            if existing + saved >= 5: break
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'levantamientos')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (rid, session['usuario_rol'], 2, 1, ruta, nombre, kb, detalles_accion))
                    mysql.connection.commit()
                    cur.close()
                    saved += 1

        if saved > 0:
            cur = mysql.connection.cursor()
            cur.execute("SELECT ur.idusuariorol FROM tbl_usuariorol ur JOIN tbl_roles r ON r.idroles=ur.idroles WHERE r.nombrerol='Administrador'")
            admins = cur.fetchall()
            cur.execute("SELECT codigo FROM tbl_registro WHERE idregistro=%s", (rid,))
            reg = cur.fetchone()
            cur.close()
            codigo = reg['codigo'] if reg else rid
            for a in admins:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_crearnotificacion', (a['idusuariorol'],
                    f'Supervisor subió imágenes en reporte {codigo}. Pendiente de validación.', 'info', rid))
                mysql.connection.commit()
                cur.close()

        flash(f'{saved} imagen(es) subida(s) exitosamente', 'success')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': f'{saved} imagen(es) subida(s) exitosamente'})
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 400
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('supervisor.desvios'))


@supervisor_bp.route('/desvios/validar/<rid>', methods=['POST'])
@sup_required
@modulo_required(('DESVIOS', 'MIS_REPORTES'))
def validar_levantamiento(rid):
    # Verificar que el usuario es Auditor
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.nombrerol 
        FROM tbl_usuariorol ur
        JOIN tbl_roles r ON ur.idroles = r.idroles
        WHERE ur.idusuario = %s
        LIMIT 1
    """, (session['user_id'],))
    
    resultado = cur.fetchone()
    cur.close()
    
    rol_usuario = resultado['nombrerol'] if resultado else None
    
    if rol_usuario != 'Auditor':
        flash('Solo los Auditores pueden validar levantamientos de observaciones', 'error')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'Solo los Auditores pueden validar levantamientos'}), 403
        return redirect(url_for('supervisor.desvios'))
    
    try:
        decision   = request.form.get('decision')
        comentario = request.form.get('comentario', '')

        if decision == 'APROBADA':
            imagenes_ids = request.form.get('imagenes_ids', '')
            if not imagenes_ids:
                msg = 'No se recibieron imágenes para aprobar'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': msg}), 400
                flash(msg, 'error')
                return redirect(url_for('supervisor.desvios'))
            
            ids_list = [i.strip() for i in imagenes_ids.split(',') if i.strip()]

            # Eliminar imágenes no aprobadas
            imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar', '')
            if imagenes_ids_rechazar:
                for imagen_id in [i.strip() for i in imagenes_ids_rechazar.split(',') if i.strip() and i.strip() not in ids_list]:
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT rutaimagen FROM tbl_imagenregistro WHERE idimagen=%s", (imagen_id,))
                    img_row = cur.fetchone()
                    cur.close()
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_eliminarimagen', (imagen_id,))
                    mysql.connection.commit()
                    cur.close()
                    if img_row: 
                        delete_image_file(img_row.get('rutaimagen', ''))

            # Aprobar imágenes seleccionadas
            for imagen_id in ids_list:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_validarimagen', (imagen_id, rid, session['usuario_rol'], 'APROBADA', comentario))
                mysql.connection.commit()
                cur.close()
            
            # Cambiar estado automáticamente a CULMINADO
            evento_resultado = EventosWorkflow.admin_aprueba_imagenes(rid, session['usuario_rol'])
            
            msg = f'{len(ids_list)} imagen(es) aprobada(s) correctamente. {evento_resultado["mensaje"]}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': msg})
            flash(msg, 'success')

        else:  # RECHAZADA
            imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar', '')
            if not imagenes_ids_rechazar:
                msg = 'No se recibieron imágenes para rechazar'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': msg}), 400
                flash(msg, 'error')
                return redirect(url_for('supervisor.desvios'))
            
            ids_list = [i.strip() for i in imagenes_ids_rechazar.split(',') if i.strip()]

            rutas = {}
            if ids_list:
                cur = mysql.connection.cursor()
                cur.execute("SELECT idimagen, rutaimagen FROM tbl_imagenregistro WHERE idimagen IN (%s)" % ','.join(['%s'] * len(ids_list)), ids_list)
                for row in cur.fetchall():
                    rutas[row['idimagen']] = row['rutaimagen']
                cur.close()

            for imagen_id in ids_list:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_validarimagen', (imagen_id, rid, session['usuario_rol'], 'RECHAZADA', comentario))
                mysql.connection.commit()
                cur.close()
                if imagen_id in rutas:
                    delete_image_file(rutas[imagen_id])

            # Cambiar estado a RECHAZADO
            evento_resultado = EventosWorkflow.admin_rechaza_imagenes(rid, session['usuario_rol'])
            
            msg = f'{len(ids_list)} imagen(es) rechazada(s). {evento_resultado["mensaje"]}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': msg})
            flash(msg, 'success')

    except Exception as e:
        msg = f'Error: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': msg}), 400
        flash(msg, 'error')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    return redirect(url_for('supervisor.desvios'))
