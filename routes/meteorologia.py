from flask import Blueprint, render_template
from utils.helpers import admin_required, modulo_required, get_notif_count

meteorologia_bp = Blueprint('meteorologia', __name__)

@meteorologia_bp.route('/meteorologia/dashboard')
@admin_required
@modulo_required('DATA_METRO_DASH')
def dashboard():
    return render_template('meteorologia/dashboard.html', notif_count=get_notif_count())

@meteorologia_bp.route('/meteorologia')
@admin_required
@modulo_required('DATA_METEOROLOGICA')
def index():
    return render_template('meteorologia/index.html', notif_count=get_notif_count())
