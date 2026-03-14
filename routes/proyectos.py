from flask import Blueprint, session, jsonify, render_template_string, request, redirect, url_for, render_template
from functools import wraps
from extensions import mysql
from utils.helpers import sp_exec
from config_proyectos import get_menu_proyecto_html, PROYECTO_DEFAULT

proyectos_bp = Blueprint('proyectos', __name__)

def login_required(f):
    """Decorador para verificar autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function

@proyectos_bp.route('/dashboard/<codigo>')
@login_required
def dashboard_proyecto(codigo):
    """Dashboard genérico para proyectos en desarrollo"""
    try:
        # Obtener información del proyecto
        cur = mysql.connection.cursor()
        proyecto = sp_exec(cur, 'sp_obtener_proyecto', (codigo,))
        cur.close()
        
        if not proyecto or len(proyecto) == 0:
            return redirect(url_for('admin.dashboard'))
        
        proyecto_data = proyecto[0]
        
        # Cambiar proyecto en sesión
        session['proyecto_actual'] = codigo
        
        return render_template('proyectos/dashboard.html', proyecto=proyecto_data)
    except Exception as e:
        print(f"ERROR en dashboard_proyecto: {str(e)}")
        return redirect(url_for('admin.dashboard'))

@proyectos_bp.route('/api/cambiar-proyecto', methods=['POST'])
@login_required
def cambiar_proyecto():
    """Cambiar el proyecto actual en la sesión"""
    try:
        data = request.get_json()
        codigo_proyecto = data.get('codigo_proyecto')
        
        if codigo_proyecto:
            # Verificar que el proyecto existe y está activo
            cur = mysql.connection.cursor()
            proyecto = sp_exec(cur, 'sp_obtener_proyecto', (codigo_proyecto,))
            cur.close()
            
            if proyecto and len(proyecto) > 0:
                proyecto_data = proyecto[0]
                if proyecto_data.get('activo') == 1:
                    session['proyecto_actual'] = codigo_proyecto
                    return jsonify({
                        'success': True,
                        'proyecto': {
                            'codigo': proyecto_data['codigo_proyecto'],
                            'nombre': proyecto_data['nombre_proyecto']
                        }
                    })
                else:
                    return jsonify({'success': False, 'error': 'Proyecto inactivo'}), 400
            else:
                return jsonify({'success': False, 'error': 'Proyecto no encontrado'}), 404
        else:
            return jsonify({'success': False, 'error': 'Código de proyecto requerido'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@proyectos_bp.route('/api/sidebar-proyecto')
@login_required
def get_sidebar_proyecto():
    """Obtener HTML del sidebar para el proyecto actual"""
    try:
        codigo_proyecto = session.get('proyecto_actual', PROYECTO_DEFAULT)
        rol = session.get('rol', 'Supervisor')
        notif_count = session.get('notif_count', 0)
        
        # El endpoint actual no está disponible en la API, se pasa vacío
        # El JavaScript puede pasar el endpoint como query param si es necesario
        request_endpoint = request.args.get('endpoint', '')
        
        # Generar HTML del sidebar usando la función de config
        html = get_menu_proyecto_html(codigo_proyecto, rol, notif_count, request_endpoint)
        
        return html
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"ERROR en get_sidebar_proyecto: {error_detail}")
        return f'<div class="error">Error: {str(e)}</div>', 500

@proyectos_bp.route('/api/proyectos-disponibles')
@login_required
def get_proyectos_disponibles():
    """Obtener lista de proyectos disponibles desde la BD"""
    try:
        print("DEBUG: Iniciando get_proyectos_disponibles")
        # Obtener proyectos activos desde la BD
        cur = mysql.connection.cursor()
        print("DEBUG: Ejecutando sp_listar_proyectos_activos")
        proyectos = sp_exec(cur, 'sp_listar_proyectos_activos')
        cur.close()
        
        print(f"DEBUG: Proyectos obtenidos: {proyectos}")
        
        proyecto_actual = session.get('proyecto_actual', PROYECTO_DEFAULT)
        
        result = {
            'success': True,
            'proyectos': [
                {
                    'id': p['id_proyecto'],
                    'codigo': p['codigo_proyecto'],
                    'nombre': p['nombre_proyecto'],
                    'descripcion': p.get('descripcion', ''),
                    'activo': p['codigo_proyecto'] == proyecto_actual,
                    'icono': p.get('icono', '📁')
                }
                for p in proyectos
            ],
            'proyecto_actual': proyecto_actual
        }
        
        print(f"DEBUG: Respuesta: {result}")
        return jsonify(result)
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"ERROR EN /api/proyectos-disponibles: {error_detail}")
        return jsonify({'success': False, 'error': str(e), 'detail': error_detail}), 500
