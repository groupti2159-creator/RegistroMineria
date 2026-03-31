import os
from flask import render_template
from utils.helpers import admin_required, modulo_required, get_notif_count
from routes.meteorologia import meteorologia_bp


@meteorologia_bp.route('/meteorologia/dashboard')
@admin_required
@modulo_required('DATA_METRO_DASH')
def dashboard():
    return render_template('meteorologia/dashboard.html',
                           notif_count=get_notif_count(),
                           wx_api_key=os.getenv('OPENWEATHER_API_KEY', ''))
