from flask import Blueprint, render_template, request
from utils.helpers import admin_required, modulo_required, get_notif_count

compromisos_bp = Blueprint('compromisos', __name__)

@compromisos_bp.route('/compromisos/dashboard')
@admin_required
@modulo_required('COMPROMISOS_DASH')
def dashboard():
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    tmpl = 'compromisos/dashboard_fragment.html' if is_ajax else 'compromisos/dashboard.html'
    return render_template(tmpl, notif_count=get_notif_count())

@compromisos_bp.route('/compromisos')
@admin_required
@modulo_required('COMPROMISOS_REG')
def index():
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    tmpl = 'compromisos/index_fragment.html' if is_ajax else 'compromisos/index.html'
    return render_template(tmpl, notif_count=get_notif_count())
