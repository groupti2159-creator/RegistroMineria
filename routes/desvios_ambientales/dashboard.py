from flask import render_template, session
from extensions import mysql
from utils.helpers import sp_exec, sp_one, admin_required, modulo_required, get_notif_count
from routes.desvios_ambientales import da_bp


@da_bp.route('/dashboard')
@admin_required
@modulo_required('DASHBOARD')
def dashboard():
    cur = mysql.connection.cursor()
    stats = sp_one(cur, 'sp_dashboardstats')
    cur.close()
    cur = mysql.connection.cursor()
    notifs = sp_exec(cur, 'sp_notificaciones', (session['usuario_rol'],))
    cur.close()
    cur = mysql.connection.cursor()
    todos = sp_exec(cur, 'sp_listarregistros', (None,))
    cur.close()

    registros_pendientes = [r for r in todos if r.get('estado') in ['Pendiente', 'Atrasado']]
    total_pendientes = len(registros_pendientes)

    return render_template('desvios_ambientales/dashboard.html',
        stats=stats or {'total': 0, 'culminados': 0, 'en_proceso': 0, 'pendientes': 0},
        notifs=notifs, notif_count=get_notif_count(),
        registros=registros_pendientes, total=total_pendientes,
        page=1, total_pages=1, per_page=total_pendientes or 10,
        estado_filter='Pendiente', personal_filter='')
