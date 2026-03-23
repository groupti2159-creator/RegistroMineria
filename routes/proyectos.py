from flask import Blueprint, session, jsonify, render_template_string, request, redirect, url_for, render_template
from functools import wraps
from extensions import mysql
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
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_proyecto WHERE codigo = %s AND activo = 1", (codigo,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return redirect(url_for('admin.dashboard'))

        proyecto_data = {
            'codigo_proyecto': row['codigo'],
            'nombre_proyecto': row['nombre'],
            'descripcion':     row.get('descripcion', ''),
            'activo':          row['activo'],
        }
        session['proyecto_actual'] = codigo
        return render_template('proyectos/dashboard.html', proyecto=proyecto_data)
    except Exception as e:
        print(f"ERROR en dashboard_proyecto: {str(e)}")
        return redirect(url_for('admin.dashboard'))

@proyectos_bp.route('/api/cambiar-proyecto', methods=['POST'])
@login_required
def cambiar_proyecto():
    try:
        data = request.get_json()
        codigo_proyecto = data.get('codigo_proyecto')

        if not codigo_proyecto:
            return jsonify({'success': False, 'error': 'Código de proyecto requerido'}), 400

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_proyecto WHERE codigo = %s AND activo = 1", (codigo_proyecto,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({'success': False, 'error': 'Proyecto no encontrado o inactivo'}), 404

        session['proyecto_actual'] = codigo_proyecto
        return jsonify({
            'success': True,
            'proyecto': {
                'codigo': row['codigo'],
                'nombre': row['nombre'],
            }
        })
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
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_proyecto WHERE activo = 1 ORDER BY nombre")
        rows = cur.fetchall() or []
        cur.close()

        proyecto_actual = session.get('proyecto_actual', PROYECTO_DEFAULT)
        return jsonify({
            'success': True,
            'proyectos': [
                {
                    'id':          p['idproyecto'],
                    'codigo':      p['codigo'],
                    'nombre':      p['nombre'],
                    'descripcion': p.get('descripcion', ''),
                    'activo':      p['codigo'] == proyecto_actual,
                    'icono':       '📁',
                }
                for p in rows
            ],
            'proyecto_actual': proyecto_actual
        })
    except Exception:
        proyecto_actual = session.get('proyecto_actual', PROYECTO_DEFAULT)
        return jsonify({
            'success': True,
            'proyectos': [{'id': 1, 'codigo': proyecto_actual, 'nombre': 'Desvíos Ambientales', 'descripcion': '', 'activo': True, 'icono': '📁'}],
            'proyecto_actual': proyecto_actual
        })
