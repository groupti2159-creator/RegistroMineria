from flask import Blueprint, render_template
from utils.helpers import admin_required, modulo_required, get_notif_count

gestion_aguas_bp = Blueprint('gestion_aguas', __name__)

@gestion_aguas_bp.route('/aguas/dashboard')
@admin_required
@modulo_required('AGUAS_DASHBOARD')
def dashboard():
    return render_template('gestion_aguas/aguas_dashboard.html',
        stats={'total_efluentes': 0, 'total_ptard': 0, 'total_ptap': 0, 'total_ana': 0},
        ultimos_registros=[],
        notif_count=get_notif_count())

@gestion_aguas_bp.route('/aguas')
@admin_required
@modulo_required('MONITOREO_AMBIENTAL')
def monitoreo_ambiental():
    return render_template('gestion_aguas/monitoreo_ambiental.html',
        registros_efluentes=[],
        registros_ptard=[],
        registros_ptap=[],
        efluentes=[],
        supervisores=[],
        notif_count=get_notif_count())

@gestion_aguas_bp.route('/ana')
@admin_required
@modulo_required('REPORTE_ANA')
def reporte_ana():
    return render_template('gestion_aguas/reporte_ana.html',
        registros=[],
        notif_count=get_notif_count())