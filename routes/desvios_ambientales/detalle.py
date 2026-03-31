from flask import request, redirect, url_for, session, flash, jsonify
from extensions import mysql
from utils.helpers import sp_exec, sp_one, admin_required, modulo_required, delete_image_file
from routes.desvios_ambientales import da_bp


@da_bp.route('/desvios/detalle/<rid>')
@admin_required
@modulo_required('DESVIOS')
def detalle_registro(rid):
    cur = mysql.connection.cursor()
    registro = sp_one(cur, 'sp_detalleregistro', (rid,))
    cur.close()
    cur = mysql.connection.cursor()
    imagenes = sp_exec(cur, 'sp_imagenesregistro', (rid,))
    cur.close()

    def serialize(obj):
        if obj is None: return {}
        return {k.lower(): (v.strftime('%Y-%m-%d') if hasattr(v, 'strftime') else (v if v is not None else ''))
                for k, v in obj.items()}

    imgs_serial    = [serialize(i) for i in imagenes if i.get('idEstadoImagen') != 3]
    return jsonify({
        'registro':       serialize(registro),
        'evidencias':     [i for i in imgs_serial if i.get('idtipoimagen') == 1],
        'levantamientos': [i for i in imgs_serial if i.get('idtipoimagen') == 2]
    })


@da_bp.route('/desvios/validar/<rid>', methods=['POST'])
@admin_required
@modulo_required('DESVIOS')
def validar_levantamiento(rid):
    try:
        decision   = request.form.get('decision')
        comentario = request.form.get('comentario', '')

        if decision == 'APROBADA':
            imagenes_ids = request.form.get('imagenes_ids', '')
            if not imagenes_ids:
                flash('No se recibieron imagenes para aprobar', 'error')
                return redirect(url_for('da.registrar'))
            ids_list = [i.strip() for i in imagenes_ids.split(',') if i.strip()]

            imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar', '')
            if imagenes_ids_rechazar:
                for imagen_id in [i.strip() for i in imagenes_ids_rechazar.split(',') if i.strip() and i.strip() not in ids_list]:
                    cur = mysql.connection.cursor()
                    cur.execute("SELECT rutaimagen FROM tbl_imagenregistro WHERE idimagen=%s", (imagen_id,))
                    img_row = cur.fetchone()
                    cur.close()
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_eliminarimagen', (imagen_id,))
                    mysql.connection.commit()
                    cur.close()
                    if img_row: delete_image_file(img_row.get('rutaimagen', ''))

            for imagen_id in ids_list:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_validarimagen', (imagen_id, rid, session['usuario_rol'], 'APROBADA', comentario))
                mysql.connection.commit()
                cur.close()
            flash(f'{len(ids_list)} imagen(es) aprobada(s) correctamente', 'success')

        else:
            imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar', '')
            if not imagenes_ids_rechazar:
                flash('No se recibieron imagenes para rechazar', 'error')
                return redirect(url_for('da.registrar'))
            ids_list = [i.strip() for i in imagenes_ids_rechazar.split(',') if i.strip()]

            rutas = {}
            if ids_list:
                cur = mysql.connection.cursor()
                cur.execute("SELECT idimagen, rutaimagen FROM tbl_imagenregistro WHERE idimagen IN (%s)" % ','.join(['%s'] * len(ids_list)), ids_list)
                for row in cur.fetchall():
                    rutas[str(row['idimagen'])] = row.get('rutaimagen', '')
                cur.close()

            for imagen_id in ids_list:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_validarimagen', (imagen_id, rid, session['usuario_rol'], 'RECHAZADA', comentario))
                mysql.connection.commit()
                cur.close()
                delete_image_file(rutas.get(imagen_id, ''))
            flash(f'{len(ids_list)} imagen(es) rechazada(s). El supervisor debe volver a subir imagenes', 'warning')

        # Notificar al supervisor
        imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar', '')
        if imagenes_ids_rechazar:
            ids_notif = [i.strip() for i in imagenes_ids_rechazar.split(',') if i.strip()]
            cur = mysql.connection.cursor()
            cur.execute("SELECT DISTINCT idusuariorol FROM tbl_imagenregistro WHERE idimagen IN (%s)" % ','.join(['%s'] * len(ids_notif)), ids_notif)
            usuarios = cur.fetchall()
            cur.close()
            for usuario in usuarios:
                msg = f'Tu conjunto de imagenes fue {"APROBADO" if decision == "APROBADA" else "RECHAZADO"}'
                if comentario: msg += f': {comentario}'
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_crearnotificacion', (usuario['idusuariorol'], msg,
                    'success' if decision == 'APROBADA' else 'warning', rid))
                mysql.connection.commit()
                cur.close()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': f'Imagenes {"aprobadas" if decision == "APROBADA" else "rechazadas"} exitosamente'})
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 400
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('da.registrar'))
