from flask import Blueprint, render_template, request
from utils.helpers import admin_required, modulo_required, get_notif_count

gr_bp = Blueprint('gr', __name__)

def _render(tmpl_name, **kwargs):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    folder, name = tmpl_name.split('/')
    tmpl = f'{folder}/{name}_fragment.html' if is_ajax else tmpl_name
    return render_template(tmpl, **kwargs)

@gr_bp.route('/residuos/dashboard')
@admin_required
@modulo_required('GR_DASHBOARD')
def dashboard():
    return _render('gestion_residuos/dashboard.html', notif_count=get_notif_count())

@gr_bp.route('/residuos/generacion')
@admin_required
@modulo_required('GENERACION_DIARIA')
def generacion():
    return _render('gestion_residuos/generacion.html', notif_count=get_notif_count())

@gr_bp.route('/residuos/comercializable')
@admin_required
@modulo_required('COMERCIALIZABLE')
def comercializable():
    return _render('gestion_residuos/comercializable.html', notif_count=get_notif_count())

@gr_bp.route('/residuos/matpel')
@admin_required
@modulo_required('DISPOSICION_MATPEL')
def matpel():
    return _render('gestion_residuos/matpel.html', notif_count=get_notif_count())

@gr_bp.route('/residuos/compostaje')
@admin_required
@modulo_required('COMPOSTAJE')
def compostaje():
    return _render('gestion_residuos/compostaje.html', notif_count=get_notif_count())
