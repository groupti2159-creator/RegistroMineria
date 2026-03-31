from flask import render_template, request, jsonify, session
from extensions import mysql
from utils.helpers import admin_required, modulo_required, get_notif_count, sp_exec, sp_one
from decimal import Decimal
from datetime import date, datetime
from routes.gestion_residuos import gr_bp


def _serialize(v):
    if isinstance(v, Decimal): return float(v)
    if isinstance(v, (date, datetime)): return v.isoformat()
    return v


@gr_bp.route('/residuos/comercializable')
@admin_required
@modulo_required('COMERCIALIZABLE')
def comercializable():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_comercializable ORDER BY fecha DESC")
    rows = cur.fetchall() or []
    cur.close()
    registros = [{k.lower(): _serialize(v) for k, v in r.items()} for r in rows]
    return render_template('gestion_residuos/comercializable.html',
                           notif_count=get_notif_count(), registros=registros)


@gr_bp.route('/residuos/comercializable/guardar', methods=['POST'])
@admin_required
def comercializable_guardar():
    d = request.get_json() or {}
    try:
        cur = mysql.connection.cursor()
        row = sp_one(cur, 'SP_Comercializable_Guardar', (
            d.get('fecha'), d.get('supervisor'), d.get('tipo'),
            d.get('precio') or None, d.get('guia'), d.get('factura'),
            d.get('peso') or None, d.get('obs'), session.get('user_id')
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'id': row['id'] if row else None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@gr_bp.route('/residuos/comercializable/editar/<int:rid>', methods=['POST'])
@admin_required
def comercializable_editar(rid):
    d = request.get_json() or {}
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'SP_Comercializable_Editar', (
            rid, d.get('fecha'), d.get('supervisor'), d.get('tipo'),
            d.get('precio') or None, d.get('guia'), d.get('factura'),
            d.get('peso') or None, d.get('obs')
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@gr_bp.route('/residuos/comercializable/eliminar/<int:rid>', methods=['POST'])
@admin_required
def comercializable_eliminar(rid):
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'SP_Comercializable_Eliminar', (rid,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
