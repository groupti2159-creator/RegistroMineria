from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from extensions import mysql
from utils.helpers import gen_id, save_image, sp_exec, sp_one

supervisor_bp = Blueprint('supervisor', __name__)

def sup_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('rol') not in ('Supervisor','Trabajador'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def get_notif_count():
    try:
        cur  = mysql.connection.cursor()
        rows = sp_exec(cur, 'SP_ContarNotificaciones', (session['usuario_rol'],))
        cur.close()
        return rows[0]['total'] if rows else 0
    except:
        return 0

@supervisor_bp.route('/desvios')
@sup_required
def desvios():
    estado_filter = request.args.get('estado','')
    cur = mysql.connection.cursor()
    registros = sp_exec(cur, 'SP_ListarRegistrosSupervisor', (estado_filter or None,))
    cur.close()
    
    cur = mysql.connection.cursor()
    notifs = sp_exec(cur, 'SP_Notificaciones', (session['usuario_rol'],))
    cur.close()
    
    return render_template('supervisor/desvios.html',
        registros=registros, notifs=notifs,
        estado_filter=estado_filter, notif_count=get_notif_count())

@supervisor_bp.route('/desvios/detalle/<rid>')
@sup_required
def detalle_registro(rid):
    cur = mysql.connection.cursor()
    registro = sp_one(cur, 'SP_DetalleRegistro', (rid,))
    cur.close()
    
    cur = mysql.connection.cursor()
    imagenes = sp_exec(cur, 'SP_ImagenesRegistro', (rid,))
    cur.close()

    def serialize(obj):
        if obj is None: return {}
        out = {}
        for k, v in obj.items():
            if hasattr(v, 'strftime'):
                out[k] = v.strftime('%Y-%m-%d ')
            else:
                out[k] = v if v is not None else ''
        return out

    # Filtrar solo imágenes que NO estén rechazadas (EIM003)
    imgs_serial = []
    for i in imagenes:
        if i.get('idEstadoImagen') != 'EIM003':  # Excluir rechazadas
            imgs_serial.append(serialize(i))

    return jsonify({
        'registro':       serialize(registro),
        'evidencias':     [i for i in imgs_serial if i.get('idTipoImagen')=='TIM001'],
        'levantamientos': [i for i in imgs_serial if i.get('idTipoImagen')=='TIM002']
    })

@supervisor_bp.route('/desvios/subir/<rid>', methods=['POST'])
@sup_required
def subir_levantamiento(rid):
    try:
        # NOTA: Actualmente solo se permite subir imágenes cuando el estado es PENDIENTE
        # Si el cliente quiere permitir subir más imágenes después de aprobar,
        # descomentar la siguiente validación y ajustar la lógica del stored procedure
        
        # Verificar estado actual (opcional - descomentar si se necesita validación)
        # cur = mysql.connection.cursor()
        # cur.execute("SELECT idEstado FROM Tbl_Registro WHERE IdRegistro=%s", (rid,))
        # registro = cur.fetchone()
        # cur.close()
        # if registro and registro['idEstado'] not in ('EST001',):  # Solo PENDIENTE
        #     flash('No se pueden subir imágenes en este estado', 'error')
        #     return redirect(url_for('supervisor.desvios'))
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) AS cnt FROM Tbl_ImagenRegistro WHERE IdRegistro=%s AND idTipoImagen='TIM002' AND idEstadoImagen != 'EIM003'", (rid,))
        cnt_row = cur.fetchone()
        existing = cnt_row['cnt'] if cnt_row else 0
        cur.close()

        files = request.files.getlist('imagenes')
        saved = 0
        for f in files:
            if existing + saved >= 5:
                break
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'levantamientos')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'SP_GuardarImagen', (gen_id(), rid, session['usuario_rol'], 'TIM002','EIM001', ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()
                    saved += 1

        if saved > 0:
            # El stored procedure SP_GuardarImagen ya cambia el estado a EN PROCESO (EST003)
            cur = mysql.connection.cursor()
            cur.execute("SELECT ur.IdUsuarioRol FROM Tbl_UsuarioRol ur JOIN Tbl_Roles r ON r.idRoles=ur.idRoles WHERE r.NombreRol='Administrador'")
            admins = cur.fetchall()
            cur.close()
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT Codigo FROM Tbl_Registro WHERE IdRegistro=%s", (rid,))
            reg = cur.fetchone()
            cur.close()
            
            codigo = reg['Codigo'] if reg else rid
            for a in admins:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'SP_CrearNotificacion', (gen_id(), a['IdUsuarioRol'],
                    f'Supervisor subió imágenes en reporte {codigo}. Pendiente de validación.', 'info', rid))
                mysql.connection.commit()
                cur.close()

        flash(f'{saved} imagen(es) subida(s) exitosamente', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('supervisor.desvios'))

@supervisor_bp.route('/historial')
@sup_required
def historial():
    cur       = mysql.connection.cursor()
    registros = sp_exec(cur, 'SP_HistorialSupervisor', (session['usuario_rol'],))
    cur.close()
    return render_template('supervisor/historial.html', registros=registros, notif_count=get_notif_count())

@supervisor_bp.route('/notificaciones/leer/<nid>', methods=['POST'])
@sup_required
def leer_notificacion(nid):
    cur = mysql.connection.cursor()
    sp_exec(cur, 'SP_LeerNotificacion', (nid,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})

@supervisor_bp.route('/notificaciones/todas', methods=['POST'])
@sup_required
def leer_todas():
    cur = mysql.connection.cursor()
    cur.execute("UPDATE Tbl_Notificacion SET Leida=1 WHERE IdUsuarioRol=%s", (session['usuario_rol'],))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})
