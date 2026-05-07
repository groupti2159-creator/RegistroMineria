from flask import render_template, request, redirect, url_for, session, flash, jsonify
from extensions import mysql
from utils.helpers import save_image, sp_exec, sp_one, admin_required, modulo_required, get_notif_count
from datetime import datetime
from routes.desvios_ambientales import da_bp


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


@da_bp.route('/desvios')
@admin_required
def desvios_redirect():
    return redirect(url_for('da.registrar', **request.args))


@da_bp.route('/registrar')
@admin_required
@modulo_required('DESVIOS')
def registrar():
    estado_filter   = request.args.get('estado', '')
    personal_filter = request.args.get('personal', '')
    page     = request.args.get('page', 1, type=int)
    per_page = 10

    cur = mysql.connection.cursor()
    todos_registros = sp_exec(cur, 'sp_listarregistros', (None,))
    cur.close()
    estados_unicos = sorted(list(set([r.get('estado', '') for r in todos_registros if r.get('estado')])))

    cur = mysql.connection.cursor()
    registros = sp_exec(cur, 'sp_listarregistros', (estado_filter or None,))
    cur.close()

    if personal_filter:
        registros = [r for r in registros if r.get('personalresponsable', '').lower() == personal_filter.lower()]

    orden_estados = {'Pendiente': 1, 'Atrasado': 2, 'Asignado': 3, 'En Proceso': 4,
                     'Enviado': 5, 'En Revision': 6, 'Culminado': 7, 'Rechazado': 8, 'Cerrado': 9}
    registros_ordenados = sorted(registros, key=lambda x: orden_estados.get(x.get('estado', ''), 999))

    total       = len(registros_ordenados)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page        = max(1, min(page, total_pages))
    start       = (page - 1) * per_page

    areas_rep, areas_res, ubicaciones, riesgos, tipos, estados = get_maestros()
    return render_template('desvios_ambientales/desvios.html',
        registros=registros_ordenados[start:start + per_page],
        areas_rep=areas_rep, areas_res=areas_res,
        ubicaciones=ubicaciones, riesgos=riesgos, tipos=tipos, estados=estados,
        estado_filter=estado_filter, personal_filter=personal_filter,
        notif_count=get_notif_count(),
        page=page, total_pages=total_pages, total=total, per_page=per_page,
        estados_unicos=estados_unicos)


@da_bp.route('/desvios/crear', methods=['POST'])
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
            request.form.get('fecha_inicio') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            request.form.get('fecha_ejecucion') or None,
            request.form['descripcion'], request.form.get('accion', ''),
            int(request.form['area_reportante']),
            int(request.form.get('personal_reportante', 0)) or None,
            int(request.form['area_responsable']),
            request.form['ubicacion'],  # Ahora es texto
            int(request.form['riesgo']), 
            int(request.form['tipo']),
            int(request.form.get('riesgo_critico', 0)) or None,
            1,  # estado inicial
            session['usuario_rol'],
            int(request.form.get('personal_responsable_id', 0)) or None,
            int(request.form['ccta_responsable']) if request.form.get('ccta_responsable') else 0,
            request.form.get('dni_responsable', '').strip()
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

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Reporte creado exitosamente', 'registro_id': rid, 'codigo': codigo})
        flash('Reporte creado exitosamente', 'success')
    except Exception as e:
        import traceback; traceback.print_exc()
        msg = f'Error al crear reporte: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': msg}), 400
        flash(msg, 'error')
    return redirect(url_for('da.registrar'))


@da_bp.route('/desvios/editar/<rid>', methods=['POST'])
@admin_required
@modulo_required('DESVIOS')
def editar_registro(rid):
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_actualizarregistro', (
            rid,
            request.form.get('fecha_inicio') or datetime.now().strftime('%Y-%m-%d'),
            request.form.get('fecha_ejecucion') or None,
            request.form['descripcion'], request.form.get('accion', ''),
            int(request.form['area_reportante']), int(request.form['area_responsable']),
            int(request.form['ubicacion']), int(request.form['riesgo']), int(request.form['tipo']),
            int(request.form['estado']),
            request.form.get('personal_responsable', ''),
            int(request.form['ccta_responsable']) if request.form.get('ccta_responsable', '').strip() not in ('', '0', 'None') else 0,
            request.form.get('dni_responsable', '').strip()
        ))
        mysql.connection.commit()
        cur.close()

        from utils.helpers import delete_image_file
        imagenes_eliminar = request.form.get('imagenes_eliminar', '')
        if imagenes_eliminar:
            for imagen_id in [i.strip() for i in imagenes_eliminar.split(',') if i.strip()]:
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

        for f in request.files.getlist('nuevas_evidencias')[:5]:
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'evidencias')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (rid, session['usuario_rol'], 1, 1, ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()

        for f in request.files.getlist('nuevos_levantamientos')[:5]:
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'levantamientos')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (rid, session['usuario_rol'], 2, 1, ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()

        flash('Reporte actualizado', 'success')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': 'Reporte actualizado exitosamente'})
    except Exception as e:
        import traceback; traceback.print_exc()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': f'Error: {str(e)}', 'traceback': traceback.format_exc()}), 400
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('da.registrar'))


@da_bp.route('/desvios/eliminar/<rid>', methods=['POST'])
@admin_required
@modulo_required('DESVIOS')
def eliminar_registro(rid):
    import os
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT rutaimagen FROM tbl_imagenregistro WHERE idregistro=%s", (rid,))
        imagenes = cur.fetchall()
        cur.execute("DELETE FROM tbl_historialaprobacion WHERE idregistro=%s", (rid,))
        cur.execute("DELETE FROM tbl_notificacion WHERE idregistro=%s", (rid,))
        cur.execute("DELETE FROM tbl_registro WHERE idregistro=%s", (rid,))
        mysql.connection.commit()
        cur.close()
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        for img in imagenes:
            ruta = img.get('rutaimagen', '')
            if ruta:
                filepath = os.path.normpath(os.path.join(base_dir, 'static', ruta))
                try:
                    if os.path.exists(filepath): os.remove(filepath)
                except Exception: pass
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        flash('Registro eliminado', 'success')
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
        flash(f'Error al eliminar: {str(e)}', 'error')
    return redirect(url_for('da.registrar'))
