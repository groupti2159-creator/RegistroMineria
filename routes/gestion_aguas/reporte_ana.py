from flask import render_template, request, redirect, url_for, jsonify
from extensions import mysql
from utils.helpers import sp_exec, get_notif_count
from routes.gestion_aguas import gestion_aguas_bp, _login_required, _num, _serializar

@gestion_aguas_bp.route('/ana')
@_login_required
def reporte_ana():
    cur = mysql.connection.cursor()
    registros = sp_exec(cur, 'sp_listarregistrosana')
    cur.close()
    return render_template('gestion_aguas/reporte_ana.html',
        registros=registros,
        notif_count=get_notif_count())

@gestion_aguas_bp.route('/ana/crear', methods=['POST'])
@_login_required
def crear_ana():
    f = request.form
    try:
        cont_ini = _num(f.get('contometro_inicial'))
        cont_fin = _num(f.get('contometro_final'))
        volumen  = round(cont_fin - cont_ini, 4) if (cont_ini is not None and cont_fin is not None) else None
        caudal   = round(volumen / 86400, 9)      if volumen is not None else None
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_crearregistroana', (
            f['fecha'], f.get('tiempo_operacion', '24 horas'),
            cont_ini, cont_fin, volumen, caudal,
        ))
        mysql.connection.commit()
        cur.close()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'volumen': volumen, 'caudal': caudal})
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
    return redirect(url_for('gestion_aguas.reporte_ana'))

@gestion_aguas_bp.route('/ana/eliminar/<int:rid>', methods=['POST'])
@_login_required
def eliminar_ana(rid):
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_eliminarregistroana', (rid,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@gestion_aguas_bp.route('/ana/detalle/<int:rid>')
@_login_required
def detalle_ana(rid):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Tbl_RegistroANA WHERE IdRegistroANA=%s", (rid,))
    row = cur.fetchone()
    cur.close()
    if not row:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify(_serializar(row))

@gestion_aguas_bp.route('/ana/editar/<int:rid>', methods=['POST'])
@_login_required
def editar_ana(rid):
    f = request.form
    try:
        cont_ini = _num(f.get('contometro_inicial'))
        cont_fin = _num(f.get('contometro_final'))
        volumen  = round(cont_fin - cont_ini, 4) if (cont_ini is not None and cont_fin is not None) else None
        caudal   = round(volumen / 86400, 9)      if volumen is not None else None
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_actualizarregistroana', (
            rid, f['fecha'], f.get('tiempo_operacion', '24 horas'),
            cont_ini, cont_fin, volumen, caudal,
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400