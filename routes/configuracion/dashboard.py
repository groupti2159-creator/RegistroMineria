from flask import render_template
from utils.helpers import admin_required, modulo_required, get_notif_count
from routes.configuracion import admin_bp


@admin_bp.route('/configuracion/dashboard')
@admin_required
@modulo_required('CONFIG_DASH')
def configuracion_dashboard():
    return render_template('configuracion/dashboard.html', notif_count=get_notif_count())
