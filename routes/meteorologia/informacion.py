from flask import render_template
from utils.helpers import admin_required, modulo_required, get_notif_count
from routes.meteorologia import meteorologia_bp


@meteorologia_bp.route('/meteorologia')
@admin_required
@modulo_required('DATA_METEOROLOGICA')
def index():
    return render_template('meteorologia/index.html', notif_count=get_notif_count())
