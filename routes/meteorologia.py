from flask import Blueprint, render_template, request
from utils.helpers import admin_required, modulo_required, get_notif_count

meteorologia_bp = Blueprint('meteorologia', __name__)

@meteorologia_bp.route('/meteorologia/dashboard')
@admin_required
@modulo_required('DATA_METRO_DASH')
def dashboard():
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    tmpl = 'meteorologia/dashboard_fragment.html' if is_ajax else 'meteorologia/dashboard.html'
    return render_template(tmpl, notif_count=get_notif_count())

@meteorologia_bp.route('/meteorologia')
@admin_required
@modulo_required('DATA_METRO_INFO')
def index():
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    tmpl = 'meteorologia/index_fragment.html' if is_ajax else 'meteorologia/index.html'
    return render_template(tmpl, notif_count=get_notif_count())
