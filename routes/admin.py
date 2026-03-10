from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from functools import wraps
from extensions import mysql
from utils.helpers import gen_id, save_image, sp_exec, sp_one
import io
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('rol') != 'Administrador':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def get_notif_count():
    try:
        cur = mysql.connection.cursor()
        rows = sp_exec(cur, 'sp_contarnotificaciones', (session['usuario_rol'],))
        cur.close()
        return rows[0]['total'] if rows else 0
    except:
        return 0

def get_maestros():
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT * FROM tbl_areareportante ORDER BY areareportante")
    areas_rep = cur.fetchall()
    
    cur.execute("SELECT * FROM tbl_arearesponsable ORDER BY arearesponsable")
    areas_res = cur.fetchall()
    
    cur.execute("SELECT * FROM tbl_ubicacion ORDER BY ubicacion")
    ubicaciones = cur.fetchall()
    
    cur.execute("SELECT * FROM tbl_riesgo")
    riesgos = cur.fetchall()
    
    cur.execute("SELECT * FROM tbl_descripciontipo ORDER BY descripciontipo")
    tipos = cur.fetchall()
    
    cur.execute("SELECT * FROM tbl_estado ORDER BY orden")
    estados = cur.fetchall()
    
    cur.close()
    return areas_rep, areas_res, ubicaciones, riesgos, tipos, estados

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    cur = mysql.connection.cursor()
    stats = sp_one(cur, 'sp_dashboardstats')
    cur.close()
    
    cur = mysql.connection.cursor()
    notifs = sp_exec(cur, 'sp_notificaciones', (session['usuario_rol'],))
    cur.close()
    
    return render_template('admin/dashboard.html',
        stats=stats or {'total':0,'culminados':0,'en_proceso':0,'pendientes':0},
        notifs=notifs, notif_count=get_notif_count())

@admin_bp.route('/desvios')
@admin_required
def desvios():
    estado_filter = request.args.get('estado','')
    cur       = mysql.connection.cursor()
    registros = sp_exec(cur, 'sp_listarregistros', (estado_filter or None,))
    cur.close()
    areas_rep, areas_res, ubicaciones, riesgos, tipos, estados = get_maestros()
    return render_template('admin/desvios.html',
        registros=registros, areas_rep=areas_rep, areas_res=areas_res,
        ubicaciones=ubicaciones, riesgos=riesgos, tipos=tipos, estados=estados,
        estado_filter=estado_filter, notif_count=get_notif_count())

@admin_bp.route('/desvios/crear', methods=['POST'])
@admin_required
def crear_registro():
    try:
        cur = mysql.connection.cursor()
        corr = sp_one(cur, 'sp_siguientecorrelativo')
        cur.close()
        
        codigo = corr['correlativo'] if corr else '001-01'
        rid = gen_id()

        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_crearregistro', (
            rid, codigo,
            request.form['fecha_inicio'],
            request.form.get('fecha_ejecucion') or None,
            request.form['descripcion'],
            request.form.get('accion',''),
            request.form['area_reportante'], request.form['area_responsable'],
            request.form['ubicacion'], request.form['riesgo'], request.form['tipo'],
            'EST001', session['usuario_rol'],  # Siempre inicia en PENDIENTE
            request.form.get('personal_responsable',''),
            request.form.get('ccta_responsable','')
        ))
        mysql.connection.commit()
        cur.close()

        for f in request.files.getlist('evidencias')[:5]:
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'evidencias')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (gen_id(), rid, session['usuario_rol'], 'TIM001','EIM001', ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()

        for f in request.files.getlist('levantamientos')[:5]:
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'levantamientos')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (gen_id(), rid, session['usuario_rol'], 'TIM002','EIM001', ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()

        cur = mysql.connection.cursor()
        cur.execute("SELECT ur.idusuariorol FROM tbl_usuariorol ur JOIN tbl_roles r ON r.idroles=ur.idroles WHERE r.nombrerol IN ('Supervisor','Trabajador')")
        sups = cur.fetchall()
        cur.close()
        
        for s in sups:
            cur = mysql.connection.cursor()
            sp_exec(cur, 'sp_crearnotificacion', (gen_id(), s['idusuariorol'], f'Nuevo reporte {codigo} creado', 'info', rid))
            mysql.connection.commit()
            cur.close()

        flash('Reporte creado exitosamente', 'success')
    except Exception as e:
        flash(f'Error al crear reporte: {str(e)}', 'error')
    return redirect(url_for('admin.desvios'))

@admin_bp.route('/desvios/editar/<rid>', methods=['POST'])
@admin_required
def editar_registro(rid):
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_actualizarregistro', (
            rid,
            request.form['fecha_inicio'],
            request.form.get('fecha_ejecucion') or None,
            request.form['descripcion'], request.form.get('accion',''),
            request.form['area_reportante'], request.form['area_responsable'],
            request.form['ubicacion'], request.form['riesgo'], request.form['tipo'],
            request.form['estado'],
            request.form.get('personal_responsable',''),
            request.form.get('ccta_responsable','')
        ))
        mysql.connection.commit()
        cur.close()
        
        # Manejar eliminación de imágenes
        imagenes_eliminar = request.form.get('imagenes_eliminar', '')
        if imagenes_eliminar:
            ids_eliminar = [id.strip() for id in imagenes_eliminar.split(',') if id.strip()]
            for imagen_id in ids_eliminar:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_eliminarimagen', (imagen_id,))
                mysql.connection.commit()
                cur.close()
        
        # Agregar nuevas evidencias
        for f in request.files.getlist('nuevas_evidencias')[:5]:
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'evidencias')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (gen_id(), rid, session['usuario_rol'], 'TIM001','EIM001', ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()
        
        # Agregar nuevos levantamientos
        for f in request.files.getlist('nuevos_levantamientos')[:5]:
            if f and f.filename:
                ruta, nombre, kb = save_image(f, 'static/uploads', 'levantamientos')
                if ruta:
                    cur = mysql.connection.cursor()
                    sp_exec(cur, 'sp_guardarimagen', (gen_id(), rid, session['usuario_rol'], 'TIM002','EIM001', ruta, nombre, kb))
                    mysql.connection.commit()
                    cur.close()
        
        flash('Reporte actualizado', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('admin.desvios'))

@admin_bp.route('/desvios/archivar/<rid>', methods=['POST'])
@admin_required
def archivar_registro(rid):
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_archivarregistro', (rid, session['usuario_rol']))
        mysql.connection.commit()
        cur.close()
        flash('Reporte archivado en historial', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('admin.desvios'))

@admin_bp.route('/desvios/detalle/<rid>')
@admin_required
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
            if hasattr(v, 'strftime'):
                out[k] = v.strftime('%Y-%m-%d')
            else:
                out[k] = v if v is not None else ''
        return out

    # Filtrar solo imágenes que NO estén rechazadas (EIM003)
    imgs_serial = []
    for i in imagenes:
        # Usar get() case-insensitive
        estado_img = i.get('idEstadoImagen') or i.get('idestadoimagen')
        if estado_img != 'EIM003':  # Excluir rechazadas
            imgs_serial.append(serialize(i))

    # Separar por tipo usando get() case-insensitive
    evidencias = []
    levantamientos = []
    for img in imgs_serial:
        tipo_img = img.get('idTipoImagen') or img.get('idtipoimagen')
        if tipo_img == 'TIM001':
            evidencias.append(img)
        elif tipo_img == 'TIM002':
            levantamientos.append(img)

    result = {
        'registro': serialize(registro),
        'evidencias': evidencias,
        'levantamientos': levantamientos
    }
    
    return jsonify(result)

@admin_bp.route('/desvios/validar/<rid>', methods=['POST'])
@admin_required
def validar_levantamiento(rid):
    try:
        decision = request.form.get('decision')
        comentario = request.form.get('comentario','')
        
        if decision == 'APROBADA':
            # APROBAR: Solo las imágenes que quedaron en el modal
            imagenes_ids = request.form.get('imagenes_ids','')
            if not imagenes_ids:
                flash('No se recibieron imágenes para aprobar', 'error')
                return redirect(url_for('admin.desvios'))
            
            ids_list = [id.strip() for id in imagenes_ids.split(',') if id.strip()]
            
            # Primero: ELIMINAR físicamente las imágenes que fueron quitadas con X
            imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar','')
            if imagenes_ids_rechazar:
                ids_rechazar_list = [id.strip() for id in imagenes_ids_rechazar.split(',') if id.strip()]
                ids_eliminar = [id for id in ids_rechazar_list if id not in ids_list]
                
                for imagen_id in ids_eliminar:
                    cur = mysql.connection.cursor()
                    # Eliminar físicamente la imagen
                    sp_exec(cur, 'sp_eliminarimagen', (imagen_id,))
                    mysql.connection.commit()
                    cur.close()
            
            # Segundo: Aprobar las imágenes seleccionadas (esto cambia estado a COMPLETADO)
            for imagen_id in ids_list:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_validarimagen', (gen_id(), imagen_id, rid, session['usuario_rol'], 'APROBADA', comentario))
                mysql.connection.commit()
                cur.close()
            
            cantidad = len(ids_list)
            flash(f'{cantidad} imagen(es) aprobada(s) correctamente', 'success')
            
        else:
            # RECHAZAR: TODAS las imágenes originales
            imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar','')
            if not imagenes_ids_rechazar:
                flash('No se recibieron imágenes para rechazar', 'error')
                return redirect(url_for('admin.desvios'))
            
            ids_list = [id.strip() for id in imagenes_ids_rechazar.split(',') if id.strip()]
            
            # Rechazar todas las imágenes originales (esto cambia estado a PENDIENTE)
            for imagen_id in ids_list:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_validarimagen', (gen_id(), imagen_id, rid, session['usuario_rol'], 'RECHAZADA', comentario))
                mysql.connection.commit()
                cur.close()
            
            cantidad = len(ids_list)
            flash(f'{cantidad} imagen(es) rechazada(s). El supervisor debe volver a subir imágenes', 'warning')
        
        # Obtener usuarios para notificar
        imagenes_ids_rechazar = request.form.get('imagenes_ids_rechazar','')
        if imagenes_ids_rechazar:
            ids_notif = [id.strip() for id in imagenes_ids_rechazar.split(',') if id.strip()]
            cur = mysql.connection.cursor()
            cur.execute("SELECT DISTINCT idusuariorol FROM tbl_imagenregistro WHERE idimagen IN (%s)" % ','.join(['%s']*len(ids_notif)), ids_notif)
            usuarios = cur.fetchall()
            cur.close()
            
            # Enviar notificación
            for usuario in usuarios:
                msg = f'Tu conjunto de imágenes fue {"APROBADO" if decision=="APROBADA" else "RECHAZADO"}'
                if comentario: 
                    msg += f': {comentario}'
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_crearnotificacion', (gen_id(), usuario['idusuariorol'], msg,
                        'success' if decision=='APROBADA' else 'warning', rid))
                mysql.connection.commit()
                cur.close()
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('admin.desvios'))

@admin_bp.route('/historial')
@admin_required
def historial():
    cur       = mysql.connection.cursor()
    registros = sp_exec(cur, 'sp_historialadmin')
    cur.close()
    return render_template('admin/historial.html', registros=registros, notif_count=get_notif_count())

@admin_bp.route('/exportar')
@admin_required
def exportar_excel():
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        from openpyxl.utils import get_column_letter
        from openpyxl.drawing.image import Image as XLImage
        from PIL import Image as PILImage
        import os
        import tempfile
        
        # Obtener registros
        cur  = mysql.connection.cursor()
        rows = sp_exec(cur, 'sp_exportarregistros')
        cur.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Desvíos Ambientales"
        hfill = PatternFill("solid", fgColor="1a7a3c")
        hfont = Font(bold=True, color="FFFFFF", size=11)
        thin  = Border(left=Side(style='thin'),right=Side(style='thin'),
                       top=Side(style='thin'),bottom=Side(style='thin'))
        
        # Headers
        headers = ['Código','Fecha','Fecha Ejecución','Área Reportante','Ubicación',
                   'Descripción','Tipo','Riesgo','Estado','Acción',
                   'Área Responsable','Personal Responsable','Fecha Creación',
                   'Evidencias','Levantamientos']
        col_w   = [12,14,16,20,30,40,30,12,14,40,22,22,18,25,25]
        
        for i,(h,w) in enumerate(zip(headers,col_w),1):
            c = ws.cell(row=1,column=i,value=h)
            c.fill=hfill; c.font=hfont; c.border=thin
            c.alignment=Alignment(horizontal='center',vertical='center')
            ws.column_dimensions[get_column_letter(i)].width=w
        
        alt = PatternFill("solid", fgColor="f0f9f4")
        current_row = 2
        
        # Lista para guardar archivos temporales y limpiarlos al final
        temp_files = []
        
        for row in rows:
            # Obtener imágenes del registro
            cur = mysql.connection.cursor()
            imagenes = sp_exec(cur, 'sp_imagenesregistro', (row.get('IdRegistro',''),))
            cur.close()
            
            # Filtrar imágenes no rechazadas
            evidencias = []
            levantamientos = []
            for img in imagenes:
                if img.get('idEstadoImagen') != 'EIM003':  # Excluir rechazadas
                    if img.get('idTipoImagen') == 'TIM001':
                        evidencias.append(img.get('RutaImagen',''))
                    elif img.get('idTipoImagen') == 'TIM002':
                        levantamientos.append(img.get('RutaImagen',''))
            
            # Calcular cuántas filas necesitamos
            max_images = max(len(evidencias), len(levantamientos), 1)
            
            # Datos del registro
            vals=[row.get('Codigo',''),row.get('Fecha',''),row.get('FechaEjecucion',''),
                  row.get('AreaReportante',''),row.get('Ubicacion',''),row.get('Descripcion',''),
                  row.get('DescripcionTipo',''),row.get('Riesgo',''),row.get('Estado',''),
                  row.get('Accion',''),row.get('AreaResponsable',''),
                  row.get('PersonalResponsable',''),row.get('FechaCreacion','')]
            
            # Escribir datos del registro en la primera fila
            for ci,v in enumerate(vals,1):
                c=ws.cell(row=current_row,column=ci,value=str(v) if v else '')
                c.border=thin
                c.alignment=Alignment(vertical='center',wrap_text=True)
                if current_row%2==0: c.fill=alt
                
                # Si hay múltiples imágenes, hacer merge de celdas verticalmente
                if max_images > 1:
                    ws.merge_cells(start_row=current_row, start_column=ci, 
                                  end_row=current_row+max_images-1, end_column=ci)
            
            # Insertar imágenes en filas separadas
            for img_idx in range(max_images):
                img_row = current_row + img_idx
                
                # Ajustar altura de fila para imágenes
                ws.row_dimensions[img_row].height = 100
                
                # Insertar evidencia si existe
                if img_idx < len(evidencias):
                    img_path = evidencias[img_idx]
                    
                    # Probar diferentes rutas posibles
                    possible_paths = [
                        img_path,
                        os.path.join('ecosupervisor', img_path),
                        os.path.join('static', img_path.replace('static/', '')),
                        os.path.join('ecosupervisor', 'static', img_path.replace('static/', ''))
                    ]
                    
                    full_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            full_path = path
                            break
                    
                    if full_path:
                        try:
                            # Crear thumbnail
                            pil_img = PILImage.open(full_path)
                            pil_img.thumbnail((80, 80), PILImage.Resampling.LANCZOS)
                            
                            # Crear archivo temporal con nombre único
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                            temp_path = temp_file.name
                            temp_file.close()
                            temp_files.append(temp_path)
                            
                            # Guardar thumbnail
                            pil_img.save(temp_path, 'PNG')
                            
                            # Insertar en Excel
                            xl_img = XLImage(temp_path)
                            cell_ref = f'{get_column_letter(14)}{img_row}'
                            ws.add_image(xl_img, cell_ref)
                            
                        except Exception as e:
                            ws.cell(row=img_row, column=14, value=f'Error: {str(e)[:30]}')
                    else:
                        ws.cell(row=img_row, column=14, value='No encontrada')
                
                # Insertar levantamiento si existe
                if img_idx < len(levantamientos):
                    img_path = levantamientos[img_idx]
                    
                    # Probar diferentes rutas posibles
                    possible_paths = [
                        img_path,
                        os.path.join('ecosupervisor', img_path),
                        os.path.join('static', img_path.replace('static/', '')),
                        os.path.join('ecosupervisor', 'static', img_path.replace('static/', ''))
                    ]
                    
                    full_path = None
                    for path in possible_paths:
                        if os.path.exists(path):
                            full_path = path
                            break
                    
                    if full_path:
                        try:
                            # Crear thumbnail
                            pil_img = PILImage.open(full_path)
                            pil_img.thumbnail((80, 80), PILImage.Resampling.LANCZOS)
                            
                            # Crear archivo temporal con nombre único
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                            temp_path = temp_file.name
                            temp_file.close()
                            temp_files.append(temp_path)
                            
                            # Guardar thumbnail
                            pil_img.save(temp_path, 'PNG')
                            
                            # Insertar en Excel
                            xl_img = XLImage(temp_path)
                            cell_ref = f'{get_column_letter(15)}{img_row}'
                            ws.add_image(xl_img, cell_ref)
                            
                        except Exception as e:
                            ws.cell(row=img_row, column=15, value=f'Error: {str(e)[:30]}')
                    else:
                        ws.cell(row=img_row, column=15, value='No encontrada')
                
                # Agregar bordes a las celdas de imágenes
                for col in [14, 15]:
                    c = ws.cell(row=img_row, column=col)
                    c.border = thin
                    if current_row%2==0: c.fill=alt
            
            # Avanzar a la siguiente fila después de todas las imágenes
            current_row += max_images
        
        # Guardar el Excel
        out=io.BytesIO()
        wb.save(out)
        out.seek(0)
        
        # Limpiar archivos temporales
        for temp_path in temp_files:
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass
        
        fname=f"desvios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        return send_file(out,download_name=fname,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True)
    except Exception as e:
        flash(f'Error al exportar: {str(e)}','error')
        return redirect(url_for('admin.desvios'))

@admin_bp.route('/notificaciones/leer/<nid>', methods=['POST'])
@admin_required
def leer_notificacion(nid):
    cur = mysql.connection.cursor()
    sp_exec(cur, 'sp_leernotificacion', (nid,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})

@admin_bp.route('/notificaciones/todas', methods=['POST'])
@admin_required
def leer_todas():
    cur = mysql.connection.cursor()
    cur.execute("UPDATE tbl_notificacion SET leida=1 WHERE idusuariorol=%s", (session['usuario_rol'],))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})
