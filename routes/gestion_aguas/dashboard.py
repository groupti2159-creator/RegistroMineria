from flask import render_template
from extensions import mysql
from utils.helpers import sp_exec, get_notif_count
from routes.gestion_aguas import gestion_aguas_bp, _login_required

@gestion_aguas_bp.route('/aguas/dashboard')
@_login_required
def aguas_dashboard():
    cur = mysql.connection.cursor()
    ef   = sp_exec(cur, 'sp_listarregistrosefluentes')
    pt   = sp_exec(cur, 'sp_listarregistrosptard')
    ptap = sp_exec(cur, 'sp_listarregistrosptap')
    ana  = sp_exec(cur, 'sp_listarregistrosana')
    cur.close()

    stats = {
        'total_efluentes': len(ef),
        'total_ptard':     len(pt),
        'total_ptap':      len(ptap),
        'total_ana':       len(ana),
    }

    ultimos = []
    for r in ef[:3]:
        ultimos.append({
            'tipo':       'Efluente',
            'fecha':      r.get('fecha'),
            'efluente':   r.get('efluente'),
            'supervisor': r.get('supervisor'),
        })
    for r in ana[:2]:
        ultimos.append({
            'tipo':       'ANA',
            'fecha':      r.get('fecha'),
            'efluente':   '—',
            'supervisor': '—',
        })

    return render_template('gestion_aguas/aguas_dashboard.html',
        stats=stats,
        ultimos=ultimos,
        notif_count=get_notif_count())