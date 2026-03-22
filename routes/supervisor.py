from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from extensions import mysql
from utils.helpers import save_image, sp_exec, sp_one

supervisor_bp = Blueprint('supervisor', __name__)

def sup_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('rol') not in ('Supervisor','Trabajador'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def modulo_required(codigo):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            if codigo not in session.get('accesos', []):
                return render_template('auth/sin_acceso.html'), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def get_notif_count():
    try:
        cur  = mysql.connection.cursor()
        rows = sp_exec(cur, 'sp_contarnotificaciones', (session['usuario_rol'],))
        cur.close()
        return rows[0]['total'] if rows else 0
    except:
        return 0

@supervisor_bp.route('/desvios')
@sup_required
@modulo_required('MIS_REPORTES')
def desvios():
    estado_filter = request.args.get('estado','')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Obtener TODOS los registros sin filtro para extraer estados únicos
    cur = mysql.connection.cursor()
    todos_registros = sp_exec(cur, 'sp_listarregistrossupervisor', (None,))
    cur.close()
    
    # Obtener estados únicos de TODOS los registros
    estados_unicos = sorted(list(set([r.get('estado', '') for r in todos_registros if r.get('estado')])))
    
    # Ahora obtener registros con filtro si aplica
    cur = mysql.connection.cursor()
    registros = sp_exec(cur, 'sp_listarregistrossupervisor', (estado_filter or None,))
    cur.close()
    
    # Definir orden de prioridad de estados
    orden_estados = {
        'Pendiente': 1,
        'En Proceso': 2,
        'Enviado': 3,
        'En Revision': 4,
        'Culminado': 5,
        'Rechazado': 6,
        'Cerrado': 7
    }
    
    # Ordenar registros por prioridad de estado
    registros_ordenados = sorted(
        registros, 
        key=lambda x: orden_estados.get(x.get('estado', ''), 999)
    )
    
    # Calcular paginación
    total = len(registros_ordenados)
    total_pages = (total + per_page - 1) // per_page  # Redondeo hacia arriba
    
    # Validar página
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Obtener registros de la página actual
    start = (page - 1) * per_page
    end = start + per_page
    registros_pagina = registros_ordenados[start:end]
    
    cur = mysql.connection.cursor()
    notifs = sp_exec(cur, 'sp_notificaciones', (session['usuario_rol'],))
    cur.close()
    
    return render_template('desvios_ambientales/supervisor_desvios.html',
        registros=registros_pagina, notifs=notifs,
        estado_filter=estado_filter, 
        notif_count=get_notif_count(),
        page=page,
        total_pages=total_pages,
        total=total,
        per_page=per_page,
        estados_unicos=estados_unicos)

@supervisor_bp.route('/desvios/detalle/<rid>')
@sup_required
@modulo_required('MIS_REPORTES')
def detalle_registro(rid):
    cur = mysql.connection.cursor()
    registro = sp_one(cur, 'sp_detalleregistro', (rid,))
    cur.close()
    
    cur = mysql.connection.cursor()
    imagenes = sp_exec(cur, 'sp_imagenesregistro', (rid,))
    cur.close()

    def serialize(obj):
        if obj is None: return {}
        out = {}
        for k, v in obj.items():
            key = k.lower()  # normalizar a minúsculas para el JS
            if hasattr(v, 'strftime'):
                out[key] = v.strftime('%Y-%m-%d ')
            else:
                out[key] = v if v is not None else ''
        return out

    # Filtrar solo imágenes que NO estén rechazadas (EIM003)
    imgs_serial = []
    for i in imagenes:
        if i.get('idEstadoImagen') != 3:
            imgs_serial.append(serialize(i))

    # Separar por tipo (claves ya en minúsculas tras serialize)
    evidencias = []
    levantamientos = []
    for img in imgs_serial:
        if img.get('idtipoimagen') == 1:
            evidencias.append(img)
        elif img.get('idtipoimagen') == 2:
            levantamientos.append(img)

    return jsonify({
        'registro': serialize(registro),
        'evidencias': evidencias,
        'levantamientos': levantamientos
    })

@supervisor_bp.route('/desvios/subir/<rid>', methods=['POST'])
@sup_required
@modulo_required('MIS_REPORTES')
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
        cur.execute("SELECT COUNT(*) AS cnt FROM tbl_imagenregistro WHERE idregistro=%s AND idtipoimagen=2 AND idestadoimagen != 3", (rid,))
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
                    sp_exec(cur, 'sp_guardarimagen', (rid, session['usuario_rol'], 2, 1, ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()
                    saved += 1

        if saved > 0:
            # El stored procedure sp_guardarimagen ya cambia el estado a EN PROCESO (EST003)
            cur = mysql.connection.cursor()
            cur.execute("SELECT ur.idusuariorol FROM tbl_usuariorol ur JOIN tbl_roles r ON r.idroles=ur.idroles WHERE r.nombrerol='Administrador'")
            admins = cur.fetchall()
            cur.close()
            
            cur = mysql.connection.cursor()
            cur.execute("SELECT codigo FROM tbl_registro WHERE idregistro=%s", (rid,))
            reg = cur.fetchone()
            cur.close()
            
            codigo = reg['codigo'] if reg else rid
            for a in admins:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_crearnotificacion', (a['idusuariorol'],
                    f'Supervisor subió imágenes en reporte {codigo}. Pendiente de validación.', 'info', rid))
                mysql.connection.commit()
                cur.close()

        flash(f'{saved} imagen(es) subida(s) exitosamente', 'success')
        
        # Soporte AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': f'{saved} imagen(es) subida(s) exitosamente'
            })
            
    except Exception as e:
        # Soporte AJAX para errores
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'error': f'Error: {str(e)}'
            }), 400
            
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('supervisor.desvios'))

@supervisor_bp.route('/notificaciones/leer/<nid>', methods=['POST'])
@sup_required
def leer_notificacion(nid):
    cur = mysql.connection.cursor()
    sp_exec(cur, 'sp_leernotificacion', (nid,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})

@supervisor_bp.route('/notificaciones/todas', methods=['POST'])
@sup_required
def leer_todas():
    cur = mysql.connection.cursor()
    cur.execute("UPDATE tbl_notificacion SET leida=1 WHERE idusuariorol=%s", (session['usuario_rol'],))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})

