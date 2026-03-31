from flask import request, send_file
from extensions import mysql
from utils.helpers import sp_exec
from routes.gestion_aguas import (gestion_aguas_bp, _login_required,
                                   excel_escribir_headers, excel_escribir_fila)
import io
import openpyxl
from datetime import datetime

@gestion_aguas_bp.route('/aguas/exportar')
@_login_required
def exportar_aguas():
    tipo = request.args.get('tipo', 'efluentes')
    cur  = mysql.connection.cursor()
    wb   = openpyxl.Workbook()
    ws   = wb.active

    if tipo == 'efluentes':
        ws.title   = "Efluentes"
        rows       = sp_exec(cur, 'sp_listarregistrosefluentes')
        headers    = ['Fecha','Efluente','Supervisor',
                      'Caudal Máx Q (l/s)','Caudal Tratado Q (l/s)',
                      'TSS','Cu Tot. (mg/l)','Pb Tot. (mg/l)','Zn Tot. (mg/l)',
                      'Fe Tot. (mg/l)','As Tot. (mg/l)','CN','Cr VI','pH Lab',
                      'TSS LMP','Cu LMP','Pb LMP','Zn LMP','Fe LMP','As LMP',
                      'CN LMP','Cr VI LMP','pH mín','pH máx']
        col_widths = [12,15,20,16,16,10,12,12,12,12,12,10,10,10,
                      10,10,10,10,10,10,10,10,10,10]
        campos     = ['fecha','efluente','supervisor','caudal_max','caudal_tratado',
                      'tss','cu_tot','pb_tot','zn_tot','fe_tot','as_tot','cn','cr_vi',
                      'ph_lab','tss_lmp','cu_lmp','pb_lmp','zn_lmp','fe_lmp','as_lmp',
                      'cn_lmp','cr_vi_lmp','ph_min','ph_max']

    elif tipo == 'ptard':
        ws.title   = "PTARD"
        rows       = sp_exec(cur, 'sp_listarregistrosptard')
        headers    = ['Fecha','Efluente','Supervisor',
                      'Caudal Máx Q (l/s)','Caudal Tratado Q (l/s)',
                      'Turbidez','Cloro','OD','pH','DBO','DQO',
                      'Turbidez LMP','Cloro LMP','OD LMP',
                      'pH 1 LMP','pH 2 LMP','DBO LMP','DQO LMP']
        col_widths = [12,15,20,16,16,12,10,10,10,10,10,14,12,10,12,12,12,12]
        campos     = ['fecha','efluente','supervisor','caudal_max','caudal_tratado',
                      'turbidez','cloro','od','ph','dbo','dqo',
                      'turbidez_lmp','cloro_lmp','od_lmp','ph1_lmp','ph2_lmp',
                      'dbo_lmp','dqo_lmp']

    else:  # ptap
        ws.title   = "PTAP"
        rows       = sp_exec(cur, 'sp_listarregistrosptap')
        headers    = ['Fecha','Efluente','Supervisor',
                      'Caudal Máx Q (l/s)','Caudal Tratado Q (l/s)',
                      'Turbidez','Cloro','OD','pH',
                      'Turbidez LMP','Cloro LMP','OD LMP','pH 1 LMP','pH 2 LMP']
        col_widths = [12,15,20,16,16,12,10,10,10,14,12,10,12,12]
        campos     = ['fecha','efluente','supervisor','caudal_max','caudal_tratado',
                      'turbidez','cloro','od','ph',
                      'turbidez_lmp','cloro_lmp','od_lmp','ph1_lmp','ph2_lmp']

    cur.close()
    excel_escribir_headers(ws, headers, col_widths)
    ws.row_dimensions[1].height = 30

    for i, row in enumerate(rows, 2):
        excel_escribir_fila(ws, i, [row.get(c, '') for c in campos])

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    fname = f"aguas_{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(out, download_name=fname,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True)