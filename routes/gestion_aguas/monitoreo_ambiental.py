from flask import render_template, request, redirect, url_for, jsonify
from extensions import mysql
from utils.helpers import sp_exec, get_notif_count
from routes.gestion_aguas import gestion_aguas_bp, _login_required, _num, _serializar


@gestion_aguas_bp.route('/aguas')
@_login_required
def monitoreo_ambiental():
    cur = mysql.connection.cursor()
    efluentes    = sp_exec(cur, 'sp_listarefluentes')
    supervisores = sp_exec(cur, 'sp_listarsupervisores')
    reg_ef       = sp_exec(cur, 'sp_listarregistrosefluentes')
    reg_ptard    = sp_exec(cur, 'sp_listarregistrosptard')
    reg_ptap     = sp_exec(cur, 'sp_listarregistrosptap')
    cur.close()
    return render_template('gestion_aguas/monitoreo_ambiental.html',
        registros_efluentes = reg_ef,
        registros_ptard     = reg_ptard,
        registros_ptap      = reg_ptap,
        efluentes           = efluentes,
        supervisores        = supervisores,
        notif_count         = get_notif_count())


# ── CREAR ────────────────────────────────────────────────

@gestion_aguas_bp.route('/aguas/crear/efluentes', methods=['POST'])
@_login_required
def crear_efluentes():
    f = request.form
    try:
        cu_tot = _num(f.get('cu_tot'))
        cn     = round(cu_tot + 0.2,  3) if cu_tot is not None else None
        cr_vi  = round(cu_tot - 0.03, 3) if cu_tot is not None else None
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_crearregistroefluentes', (
            f['fecha'], int(f['efluente']), f['supervisor'],
            _num(f.get('caudal_max')), _num(f.get('caudal_tratado')),
            _num(f.get('tss')), cu_tot,
            _num(f.get('pb_tot')), _num(f.get('zn_tot')),
            _num(f.get('fe_tot')), _num(f.get('as_tot')),
            cn, cr_vi, _num(f.get('ph_lab')),
            _num(f.get('tss_lmp')), _num(f.get('cu_lmp')),
            _num(f.get('pb_lmp')), _num(f.get('zn_lmp')),
            _num(f.get('fe_lmp')), _num(f.get('as_lmp')),
            _num(f.get('cn_lmp')), _num(f.get('cr_vi_lmp')),
            _num(f.get('ph_min')), _num(f.get('ph_max')),
        ))
        mysql.connection.commit()
        cur.close()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
    return redirect(url_for('gestion_aguas.monitoreo_ambiental'))


@gestion_aguas_bp.route('/aguas/crear/ptard', methods=['POST'])
@_login_required
def crear_ptard():
    f = request.form
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_crearregistroptard', (
            f['fecha'], int(f['efluente']), f['supervisor'],
            _num(f.get('caudal_max')), _num(f.get('caudal_tratado')),
            _num(f.get('turbidez')), _num(f.get('cloro')),
            _num(f.get('od')), _num(f.get('ph')),
            _num(f.get('dbo')), _num(f.get('dqo')),
            _num(f.get('turbidez_lmp')), _num(f.get('cloro_lmp')),
            _num(f.get('od_lmp')), _num(f.get('ph1_lmp')),
            _num(f.get('ph2_lmp')), _num(f.get('dbo_lmp')),
            _num(f.get('dqo_lmp')),
        ))
        mysql.connection.commit()
        cur.close()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
    return redirect(url_for('gestion_aguas.monitoreo_ambiental'))


@gestion_aguas_bp.route('/aguas/crear/ptap', methods=['POST'])
@_login_required
def crear_ptap():
    f = request.form
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_crearregistroptap', (
            f['fecha'], int(f['efluente']), f['supervisor'],
            _num(f.get('caudal_max')), _num(f.get('caudal_tratado')),
            _num(f.get('turbidez')), _num(f.get('cloro')),
            _num(f.get('od')), _num(f.get('ph')),
            _num(f.get('turbidez_lmp')), _num(f.get('cloro_lmp')),
            _num(f.get('od_lmp')), _num(f.get('ph1_lmp')),
            _num(f.get('ph2_lmp')),
        ))
        mysql.connection.commit()
        cur.close()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
    return redirect(url_for('gestion_aguas.monitoreo_ambiental'))


# ── EDITAR ───────────────────────────────────────────────

@gestion_aguas_bp.route('/aguas/editar/efluentes/<int:rid>', methods=['POST'])
@_login_required
def editar_efluentes(rid):
    f = request.form
    try:
        cu_tot = _num(f.get('cu_tot'))
        cn     = round(cu_tot + 0.2,  3) if cu_tot is not None else None
        cr_vi  = round(cu_tot - 0.03, 3) if cu_tot is not None else None
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_actualizarregistroefluentes', (
            rid, f['fecha'], int(f['efluente']), f['supervisor'],
            _num(f.get('caudal_max')), _num(f.get('caudal_tratado')),
            _num(f.get('tss')), cu_tot,
            _num(f.get('pb_tot')), _num(f.get('zn_tot')),
            _num(f.get('fe_tot')), _num(f.get('as_tot')),
            cn, cr_vi, _num(f.get('ph_lab')),
            _num(f.get('tss_lmp')), _num(f.get('cu_lmp')),
            _num(f.get('pb_lmp')), _num(f.get('zn_lmp')),
            _num(f.get('fe_lmp')), _num(f.get('as_lmp')),
            _num(f.get('cn_lmp')), _num(f.get('cr_vi_lmp')),
            _num(f.get('ph_min')), _num(f.get('ph_max')),
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@gestion_aguas_bp.route('/aguas/editar/ptard/<int:rid>', methods=['POST'])
@_login_required
def editar_ptard(rid):
    f = request.form
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_actualizarregistroptard', (
            rid, f['fecha'], int(f['efluente']), f['supervisor'],
            _num(f.get('caudal_max')), _num(f.get('caudal_tratado')),
            _num(f.get('turbidez')), _num(f.get('cloro')),
            _num(f.get('od')), _num(f.get('ph')),
            _num(f.get('dbo')), _num(f.get('dqo')),
            _num(f.get('turbidez_lmp')), _num(f.get('cloro_lmp')),
            _num(f.get('od_lmp')), _num(f.get('ph1_lmp')),
            _num(f.get('ph2_lmp')), _num(f.get('dbo_lmp')),
            _num(f.get('dqo_lmp')),
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@gestion_aguas_bp.route('/aguas/editar/ptap/<int:rid>', methods=['POST'])
@_login_required
def editar_ptap(rid):
    f = request.form
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_actualizarregistroptap', (
            rid, f['fecha'], int(f['efluente']), f['supervisor'],
            _num(f.get('caudal_max')), _num(f.get('caudal_tratado')),
            _num(f.get('turbidez')), _num(f.get('cloro')),
            _num(f.get('od')), _num(f.get('ph')),
            _num(f.get('turbidez_lmp')), _num(f.get('cloro_lmp')),
            _num(f.get('od_lmp')), _num(f.get('ph1_lmp')),
            _num(f.get('ph2_lmp')),
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ── ELIMINAR ─────────────────────────────────────────────

@gestion_aguas_bp.route('/aguas/eliminar/efluentes/<int:rid>', methods=['POST'])
@_login_required
def eliminar_efluentes(rid):
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_eliminarregistroefluentes', (rid,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@gestion_aguas_bp.route('/aguas/eliminar/ptard/<int:rid>', methods=['POST'])
@_login_required
def eliminar_ptard(rid):
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_eliminarregistroptard', (rid,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@gestion_aguas_bp.route('/aguas/eliminar/ptap/<int:rid>', methods=['POST'])
@_login_required
def eliminar_ptap(rid):
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_eliminarregistroptap', (rid,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ── DETALLE (tablas ya en minúscula) ─────────────────────

@gestion_aguas_bp.route('/aguas/detalle/efluentes/<int:rid>')
@_login_required
def detalle_efluentes(rid):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_registroefluentes WHERE idregistroefluentes = %s", (rid,))
        row = cur.fetchone()
        cur.close()
        if not row:
            return jsonify({'error': 'No encontrado'}), 404
        return jsonify(_serializar(row))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gestion_aguas_bp.route('/aguas/detalle/ptard/<int:rid>')
@_login_required
def detalle_ptard(rid):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_registroptard WHERE idregistroptard = %s", (rid,))
        row = cur.fetchone()
        cur.close()
        if not row:
            return jsonify({'error': 'No encontrado'}), 404
        return jsonify(_serializar(row))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@gestion_aguas_bp.route('/aguas/detalle/ptap/<int:rid>')
@_login_required
def detalle_ptap(rid):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_registroptap WHERE idregistroptap = %s", (rid,))
        row = cur.fetchone()
        cur.close()
        if not row:
            return jsonify({'error': 'No encontrado'}), 404
        return jsonify(_serializar(row))
    except Exception as e:
        return jsonify({'error': str(e)}), 500