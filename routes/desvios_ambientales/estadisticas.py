from flask import render_template, request, redirect, url_for, jsonify
from extensions import mysql
from utils.helpers import sp_exec, admin_required, modulo_required, get_notif_count
from routes.desvios_ambientales import da_bp


@da_bp.route('/estadisticas')
@admin_required
@modulo_required('ESTADISTICAS')
def estadisticas():
    return render_template('desvios_ambientales/estadisticas.html', notif_count=get_notif_count())


@da_bp.route('/estadisticas/areas')
@admin_required
@modulo_required('ESTADISTICAS')
def estadisticas_areas():
    fecha_ini = request.args.get('fecha_ini') or None
    fecha_fin = request.args.get('fecha_fin') or None
    cur = mysql.connection.cursor()
    stats = sp_exec(cur, 'sp_estadisticasareas', (fecha_ini, fecha_fin))
    cur.close()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify([dict(r) for r in stats])
    return redirect(url_for('da.estadisticas'))


@da_bp.route('/estadisticas/ccta')
@admin_required
@modulo_required('ESTADISTICAS')
def estadisticas_ccta():
    fecha_ini = request.args.get('fecha_ini') or None
    fecha_fin = request.args.get('fecha_fin') or None
    cur = mysql.connection.cursor()
    stats = sp_exec(cur, 'sp_estadisticasccta', (fecha_ini, fecha_fin))
    cur.close()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify([dict(r) for r in stats])
    return redirect(url_for('da.estadisticas'))


@da_bp.route('/estadisticas/tipos')
@admin_required
@modulo_required('ESTADISTICAS')
def estadisticas_tipos():
    fecha_ini = request.args.get('fecha_ini') or None
    fecha_fin = request.args.get('fecha_fin') or None
    cur = mysql.connection.cursor()
    stats = sp_exec(cur, 'sp_estadisticas_tipos_pendientes', (fecha_ini, fecha_fin))
    cur.close()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify([dict(r) for r in stats])
    return redirect(url_for('da.estadisticas'))
