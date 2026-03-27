from flask import render_template, request, redirect, url_for, session, jsonify, send_file
from extensions import mysql
from utils.helpers import sp_exec, sp_one, get_notif_count
from routes.compromisos import compromisos_bp, _login_required
from datetime import date
import io

@compromisos_bp.route('/compromisos')
@_login_required
def index():
    mes  = int(request.args.get('mes',  date.today().month))
    anio = int(request.args.get('anio', date.today().year))

    cur = mysql.connection.cursor()
    compromisos   = sp_exec(cur, 'sp_listarcompromisos')
    supervisores  = sp_exec(cur, 'sp_listarsupervisores')
    cumplimientos = sp_exec(cur, 'sp_obtenercumplimiento', (mes, anio))
    cur.close()

    cum_dict = {str(c['idcompromiso']): c for c in cumplimientos}

    return render_template('compromisos/registro.html',
        compromisos=compromisos,
        supervisores=supervisores,
        cum_dict=cum_dict,
        mes=mes,
        anio=anio,
        notif_count=get_notif_count())

@compromisos_bp.route('/compromisos/guardar', methods=['POST'])
@_login_required
def guardar_cumplimiento():
    try:
        data = request.get_json()
        cur  = mysql.connection.cursor()
        sp_exec(cur, 'sp_guardarcumplimiento', (
            int(data['idcompromiso']),
            int(data['mes']),
            int(data['anio']),
            data.get('idusuario', '') or '',
            data.get('observaciones', '') or '',
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@compromisos_bp.route('/compromisos/subir-evidencia', methods=['POST'])
@_login_required
def subir_evidencia():
    try:
        idcompromiso = int(request.form['idcompromiso'])
        mes          = int(request.form['mes'])
        anio         = int(request.form['anio'])
        archivo      = request.files.get('archivo')

        if not archivo or not archivo.filename:
            return jsonify({'success': False, 'error': 'No se recibió archivo'}), 400

        datos  = archivo.read()
        nombre = archivo.filename
        mime   = archivo.mimetype or 'application/octet-stream'
        tamano = len(datos) // 1024

        cur    = mysql.connection.cursor()
        result = sp_one(cur, 'sp_subirevidencia', (
            idcompromiso, mes, anio,
            nombre, mime, tamano, datos,
            session.get('user_id', ''),
        ))
        mysql.connection.commit()
        cur.close()
        return jsonify({
            'success': True,
            'version': result['version'] if result else 1,
            'nombre':  nombre,
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@compromisos_bp.route('/compromisos/descargar/<int:idcompromiso>')
@_login_required
def descargar_evidencia(idcompromiso):
    mes  = int(request.args.get('mes',  date.today().month))
    anio = int(request.args.get('anio', date.today().year))
    try:
        cur = mysql.connection.cursor()
        ev  = sp_one(cur, 'sp_descargarevidencia', (idcompromiso, mes, anio))
        cur.close()
        if not ev or not ev.get('datos'):
            return jsonify({'error': 'Sin evidencia para este período'}), 404
        return send_file(
            io.BytesIO(ev['datos']),
            download_name=ev['nombre_archivo'],
            mimetype=ev['tipo_mime'] or 'application/octet-stream',
            as_attachment=True,
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500