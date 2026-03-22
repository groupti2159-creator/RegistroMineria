from flask import Blueprint, render_template
from utils.helpers import admin_required, modulo_required, get_notif_count

compromisos_bp = Blueprint('compromisos', __name__)

@compromisos_bp.route('/compromisos/dashboard')
@admin_required
@modulo_required('COMPROMISOS_DASH')
def dashboard():
    return render_template('compromisos/dashboard.html', notif_count=get_notif_count())

@compromisos_bp.route('/compromisos')
@admin_required
@modulo_required('COMPROMISOS')
def index():
    return render_template('compromisos/registro.html', notif_count=get_notif_count())
