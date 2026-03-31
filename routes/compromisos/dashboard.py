from flask import render_template
from extensions import mysql
from utils.helpers import sp_exec, get_notif_count
from routes.compromisos import compromisos_bp, _login_required
from datetime import date

@compromisos_bp.route('/compromisos/dashboard')
@_login_required
def dashboard():
    mes  = date.today().month
    anio = date.today().year

    cur = mysql.connection.cursor()
    compromisos   = sp_exec(cur, 'sp_listarcompromisos')
    cumplimientos = sp_exec(cur, 'sp_obtenercumplimiento', (mes, anio))
    cur.close()

    total     = len(compromisos)
    cumplidos = sum(1 for c in cumplimientos
                   if c.get('tiene_evidencia') or c.get('TIENE_EVIDENCIA'))
    pendientes = total - cumplidos

    ultimos = []
    for c in cumplimientos:
        if c.get('tiene_evidencia') or c.get('TIENE_EVIDENCIA'):
            comp = next((x for x in compromisos
                        if str(x.get('idcompromiso')) == str(
                            c.get('idcompromiso') or c.get('IDCOMPROMISO'))), {})
            ultimos.append({
                'obligacion':          comp.get('nombre', '—'),
                'entidad_regulatoria': comp.get('entidad_reguladora', '—'),
                'supervisor':          c.get('idusuario') or c.get('IDUSUARIO') or '—',
                'fecha':               f"{mes}/{anio}",
            })

    return render_template('compromisos/dashboard.html',
        stats={
            'total':      total,
            'cumplidos':  cumplidos,
            'pendientes': pendientes,
            'vencidos':   0,
        },
        ultimos=ultimos[:5],
        notif_count=get_notif_count())