from flask import Blueprint, render_template, request, jsonify, session
from datetime import date, datetime
from decimal import Decimal
from extensions import mysql
from utils.helpers import admin_required, modulo_required, get_notif_count, sp_exec, sp_one

gen_bp = Blueprint('gen', __name__)

SECTIONS = [
    {"id": "gen",  "label": "RRSS Generales",       "unit": "Kg",  "en_total": True},
    {"id": "org",  "label": "RRSS Orgánicos",        "unit": "Kg",  "en_total": True},
    {"id": "ind",  "label": "RRSS Industriales",     "unit": "Kg",  "en_total": True},
    {"id": "hosp", "label": "Hospitalarios",         "unit": "Kg",  "en_total": True},
    {"id": "ace",  "label": "Aceites",               "unit": "gal", "en_total": False},
    {"id": "bor",  "label": "Borras",                "unit": "Kg",  "en_total": True},
    {"id": "cop",  "label": "Copelas",               "unit": "Kg",  "en_total": True},
    {"id": "tier", "label": "Tierra contaminada",    "unit": "Kg",  "en_total": True},
    {"id": "var",  "label": "Varios",                "unit": "Kg",  "en_total": True},
    {"id": "tar",  "label": "Tarros y res. menores", "unit": "Kg",  "en_total": True},
    {"id": "chat", "label": "Chatarra mayor",        "unit": "Kg",  "en_total": True},
    {"id": "plas", "label": "RRSS Plástico",         "unit": "Kg",  "en_total": True},
    {"id": "vid",  "label": "RRSS Vidrio",           "unit": "Kg",  "en_total": True},
    {"id": "pap",  "label": "RRSS Papel y cartón",   "unit": "Kg",  "en_total": True,
     "col_keys": ["pap_coripuno"],
     "plants":   ["CORI PUNO"]},
    {"id": "mad",  "label": "RRSS Madera",           "unit": "Kg",  "en_total": True},
]

PLANTS = ['CORI PUNO']

PLANT_COLUMN_MAP = {
    'SUNEC': 'sunec',
    'CORI PUNO': 'coripuno',
    'ANTIOQUIA': 'antioquia',
    'PARCOY': 'parcoy',
    'SANTA MARÍA': 'smaria',
}

# Columnas por sección (índice 0..n-1 = planta, índice n = total)
# Para secciones sin col_keys se usan las columnas según las plantas definidas.
def sec_cols(sec):
    """Devuelve las claves de columna para una sección."""
    if 'col_keys' in sec:
        return sec['col_keys']
    sid = sec['id']
    return [f"{sid}_{PLANT_COLUMN_MAP.get(plant, plant.lower().replace(' ', '_'))}" for plant in PLANTS]

def serialize_registro(r):
    """Convierte un registro de BD a dict JSON-serializable con claves en minúsculas."""
    out = {}
    for k, v in r.items():
        key = k.lower()
        if v is None:
            out[key] = None
        elif isinstance(v, Decimal):
            out[key] = float(v)
        elif isinstance(v, (datetime, date)):
            out[key] = v.isoformat()
        else:
            out[key] = v
    return out


COLORS = {
    'gen':  '#22c55e', 'org':  '#16a34a', 'ind':  '#3b82f6', 'hosp': '#ef4444',
    'ace':  '#a855f7', 'bor':  '#f59e0b', 'cop':  '#f97316', 'tier': '#92400e',
    'var':  '#6b7280', 'tar':  '#0891b2', 'chat': '#475569', 'plas': '#06b6d4',
    'vid':  '#10b981', 'pap':  '#8b5cf6', 'mad':  '#d97706',
}




@gen_bp.route('/residuos/generacion')
@admin_required
@modulo_required('GENERACION_DIARIA')
def generacion():
    cur = mysql.connection.cursor()
    raw = sp_exec(cur, 'sp_listar_generacion', ())
    cur.close()
    registros = [serialize_registro(r) for r in (raw or [])]

    # Recalcular totales por sección si son NULL (registros insertados manualmente)
    for r in registros:
        for sec in SECTIONS:
            sid = sec['id']
            col_keys = sec.get('col_keys', sec_cols(sec))
            total_key = sid + '_total'
            if not r.get(total_key):  # None o 0
                r[total_key] = round(sum(float(r.get(c) or 0) for c in col_keys), 2)
    return render_template(
        'gestion_residuos/generacion.html',
        sections=SECTIONS,
        plants=PLANTS,
        colors=COLORS,
        today=date.today().isoformat(),
        notif_count=get_notif_count(),
        registros=registros,
    )


@gen_bp.route('/rrss/calcular', methods=['POST'])
@admin_required
def calcular():
    data   = request.get_json() or {}
    valores = data.get('valores', {})
    secciones = {}
    total_kg  = 0.0
    for sec in SECTIONS:
        sid  = sec['id']
        unit = sec['unit']
        vals = valores.get(sid, [0, 0, 0, 0])
        total = sum(float(v) for v in vals if v)
        secciones[sid] = {'total': total, 'unit': unit}
        if sec['en_total']:
            total_kg += total
    return jsonify({
        'secciones':    secciones,
        'total_kg':     total_kg,
        'generacion_t': f'{total_kg / 1000:.3f}',
    })


@gen_bp.route('/rrss/guardar', methods=['POST'])
@admin_required
def guardar():
    data    = request.get_json() or {}
    fecha   = data.get('fecha')
    valores = data.get('valores', {})
    gen_t   = float(data.get('generacion_t', 0))

    if not fecha:
        return jsonify({'success': False, 'error': 'Fecha requerida'}), 400

    def v(sid, idx):
        row = valores.get(sid) or []
        if idx < 0 or idx >= len(row):
            return 0.0
        return float(row[idx] or 0)

    def t(sid):
        row = valores.get(sid) or []
        return sum(float(x or 0) for x in row)

    params = (
        fecha, gen_t,
        v('gen',0), v('gen',1), v('gen',2), v('gen',3), t('gen'),
        v('org',0), v('org',1), v('org',2), v('org',3), t('org'),
        v('ind',0), v('ind',1), v('ind',2), v('ind',3), t('ind'),
        v('hosp',0),v('hosp',1),v('hosp',2),v('hosp',3),t('hosp'),
        v('ace',0), v('ace',1), v('ace',2), v('ace',3), t('ace'),
        v('bor',0), v('bor',1), v('bor',2), v('bor',3), t('bor'),
        v('cop',0), v('cop',1), v('cop',2), v('cop',3), t('cop'),
        v('tier',0),v('tier',1),v('tier',2),v('tier',3),t('tier'),
        v('var',0), v('var',1), v('var',2), v('var',3), t('var'),
        v('tar',0), v('tar',1), v('tar',2), v('tar',3), t('tar'),
        v('chat',0),v('chat',1),v('chat',2),v('chat',3),t('chat'),
        v('plas',0),v('plas',1),v('plas',2),v('plas',3),t('plas'),
        v('vid',0), v('vid',1), v('vid',2), v('vid',3), t('vid'),
        v('pap',0), v('pap',1), v('pap',2), v('pap',3), t('pap'),
        v('mad',0), v('mad',1), v('mad',2), v('mad',3), t('mad'),
        session.get('user_id'),
    )

    try:
        cur = mysql.connection.cursor()
        result = sp_one(cur, 'sp_guardar_generacion', params)
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True, 'idgeneracion': result.get('idgeneracion') if result else None})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@gen_bp.route('/rrss/eliminar/<int:idgeneracion>', methods=['POST'])
@admin_required
def eliminar_generacion(idgeneracion):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM tbl_generacion_diaria WHERE idgeneracion = %s", (idgeneracion,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@gen_bp.route('/rrss/editar/<int:idgeneracion>', methods=['POST'])
@admin_required
def editar_generacion(idgeneracion):
    data    = request.get_json() or {}
    fecha   = data.get('fecha')
    valores = data.get('valores', {})
    gen_t   = float(data.get('generacion_t', 0))

    if not fecha:
        return jsonify({'success': False, 'error': 'Fecha requerida'}), 400

    def v(sid, idx):
        row = valores.get(sid) or []
        if idx < 0 or idx >= len(row):
            return 0.0
        return float(row[idx] or 0)

    def t(sid):
        return sum(float(x or 0) for x in (valores.get(sid) or []))

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE tbl_generacion_diaria SET
              fecha=%s, generacion_t=%s,
              gen_sunec=%s,  gen_coripuno=%s,  gen_antioquia=%s,  gen_parcoy=%s,  gen_total=%s,
              org_sunec=%s,  org_coripuno=%s,  org_antioquia=%s,  org_parcoy=%s,  org_total=%s,
              ind_sunec=%s,  ind_coripuno=%s,  ind_antioquia=%s,  ind_parcoy=%s,  ind_total=%s,
              hosp_sunec=%s, hosp_coripuno=%s, hosp_antioquia=%s, hosp_parcoy=%s, hosp_total=%s,
              ace_sunec=%s,  ace_coripuno=%s,  ace_antioquia=%s,  ace_parcoy=%s,  ace_total=%s,
              bor_sunec=%s,  bor_coripuno=%s,  bor_antioquia=%s,  bor_parcoy=%s,  bor_total=%s,
              cop_sunec=%s,  cop_coripuno=%s,  cop_antioquia=%s,  cop_parcoy=%s,  cop_total=%s,
              tier_sunec=%s, tier_coripuno=%s, tier_antioquia=%s, tier_parcoy=%s, tier_total=%s,
              var_sunec=%s,  var_coripuno=%s,  var_antioquia=%s,  var_parcoy=%s,  var_total=%s,
              tar_sunec=%s,  tar_coripuno=%s,  tar_antioquia=%s,  tar_parcoy=%s,  tar_total=%s,
              chat_sunec=%s, chat_coripuno=%s, chat_antioquia=%s, chat_parcoy=%s, chat_total=%s,
              plas_sunec=%s, plas_coripuno=%s, plas_antioquia=%s, plas_parcoy=%s, plas_total=%s,
              vid_sunec=%s,  vid_coripuno=%s,  vid_antioquia=%s,  vid_parcoy=%s,  vid_total=%s,
              pap_sunec=%s,  pap_coripuno=%s,  pap_antioquia=%s,  papa_smaria=%s,  pap_total=%s,
              mad_sunec=%s,  mad_coripuno=%s,  mad_antioquia=%s,  mad_parcoy=%s,  mad_total=%s
            WHERE idgeneracion=%s
        """, (
            fecha, gen_t,
            v('gen',0),  v('gen',1),  v('gen',2),  v('gen',3),  t('gen'),
            v('org',0),  v('org',1),  v('org',2),  v('org',3),  t('org'),
            v('ind',0),  v('ind',1),  v('ind',2),  v('ind',3),  t('ind'),
            v('hosp',0), v('hosp',1), v('hosp',2), v('hosp',3), t('hosp'),
            v('ace',0),  v('ace',1),  v('ace',2),  v('ace',3),  t('ace'),
            v('bor',0),  v('bor',1),  v('bor',2),  v('bor',3),  t('bor'),
            v('cop',0),  v('cop',1),  v('cop',2),  v('cop',3),  t('cop'),
            v('tier',0), v('tier',1), v('tier',2), v('tier',3), t('tier'),
            v('var',0),  v('var',1),  v('var',2),  v('var',3),  t('var'),
            v('tar',0),  v('tar',1),  v('tar',2),  v('tar',3),  t('tar'),
            v('chat',0), v('chat',1), v('chat',2), v('chat',3), t('chat'),
            v('plas',0), v('plas',1), v('plas',2), v('plas',3), t('plas'),
            v('vid',0),  v('vid',1),  v('vid',2),  v('vid',3),  t('vid'),
            v('pap',0),  v('pap',1),  v('pap',2),  v('pap',3),  t('pap'),
            v('mad',0),  v('mad',1),  v('mad',2),  v('mad',3),  t('mad'),
            idgeneracion,
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        import traceback
        return jsonify({'success': False, 'error': str(e), 'detail': traceback.format_exc()})
