from flask import send_file
from extensions import mysql
from utils.helpers import sp_exec
from routes.gestion_aguas import (gestion_aguas_bp, _login_required,
                                   excel_escribir_headers, excel_escribir_fila)
import io
import openpyxl
from datetime import datetime

@gestion_aguas_bp.route('/ana/exportar')
@_login_required
def exportar_ana():
    cur  = mysql.connection.cursor()
    rows = sp_exec(cur, 'sp_listarregistrosana')
    cur.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reportes ANA"

    headers    = ['Fecha','Tiempo de Operación',
                  'Contómetro Inicial','Contómetro Final',
                  'Volumen Captado (m³)','Caudal (m³/seg)']
    col_widths = [14, 20, 20, 20, 22, 20]
    campos     = ['fecha','tiempo_operacion',
                  'contometro_inicial','contometro_final',
                  'volumen_captado','caudal']

    excel_escribir_headers(ws, headers, col_widths)
    ws.row_dimensions[1].height = 30

    for i, row in enumerate(rows, 2):
        excel_escribir_fila(ws, i, [row.get(c, '') for c in campos])

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    fname = f"reportes_ana_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(out, download_name=fname,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True)