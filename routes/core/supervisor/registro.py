from flask import render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from extensions import mysql
from utils.helpers import save_image, sp_exec, sp_one, get_notif_count, modulo_required
from routes.core.supervisor import supervisor_bp


def sup_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('rol') not in ('Supervisor', 'Trabajador'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@supervisor_bp.route('/desvios')
@sup_required
@modulo_required('MIS_REPORTES')
def desvios():
    estado_filter = request.args.get('estado', '')
    page     = request.args.get('page', 1, type=int)
    per_page = 10

    cur = mysql.connection.cursor()
    todos_registros = sp_exec(cur, 'sp_listarregistrossupervisor', (None,))
    cur.close()
    estados_unicos = sorted(list(set([r.get('estado', '') for r in todos_registros if r.get('estado')])))

    cur = mysql.connection.cursor()
    registros = sp_exec(cur, 'sp_listarregistrossupervisor', (estado_filter or None,))
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

    return render_template('desvios_ambientales/supervisor_desvios.html',
        registros=registros_ordenados[start:start + per_page], notifs=notifs,
        estado_filter=estado_filter, notif_count=get_notif_count(),
        page=page, total_pages=total_pages, total=total, per_page=per_page,
        estados_unicos=estados_unicos)


@supervisor_bp.route('/desvios/detalle/<rid>')
@sup_required
@modulo_required('MIS_REPORTES')
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
@modulo_required('MIS_REPORTES')
def subir_levantamiento(rid):
    try:
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
                    sp_exec(cur, 'sp_guardarimagen', (rid, session['usuario_rol'], 2, 1, ruta, nombre, kb))
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
