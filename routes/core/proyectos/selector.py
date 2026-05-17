from flask import session, jsonify, request, redirect, url_for, render_template
from functools import wraps
from extensions import mysql
from config_proyectos import get_menu_proyecto_html, PROYECTO_DEFAULT
from routes.core.proyectos import proyectos_bp


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        return f(*args, **kwargs)
    return decorated_function


@proyectos_bp.route('/dashboard/<int:proyecto_id>')
@login_required
def dashboard_proyecto(proyecto_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_proyecto WHERE idproyecto = %s AND activo = 1", (proyecto_id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            return redirect(url_for('da.dashboard'))
        session['proyecto_actual'] = proyecto_id
        return render_template('proyectos/dashboard.html', proyecto={
            'id_proyecto': row['idproyecto'],
            'nombre_proyecto': row['nombre'],
            'descripcion':     row.get('descripcion', ''),
            'activo':          row['activo'],
        })
    except Exception as e:
        print(f"ERROR en dashboard_proyecto: {str(e)}")
        return redirect(url_for('da.dashboard'))


@proyectos_bp.route('/api/cambiar-proyecto', methods=['POST'])
@login_required
def cambiar_proyecto():
    try:
        data = request.get_json()
        proyecto_id = data.get('proyecto_id')
        if not proyecto_id:
            return jsonify({'success': False, 'error': 'ID de proyecto requerido'}), 400
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_proyecto WHERE idproyecto = %s AND activo = 1", (proyecto_id,))
        row = cur.fetchone()
        cur.close()
        if not row:
            return jsonify({'success': False, 'error': 'Proyecto no encontrado o inactivo'}), 404
        session['proyecto_actual'] = proyecto_id
        return jsonify({'success': True, 'proyecto': {'id': row['idproyecto'], 'nombre': row['nombre']}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@proyectos_bp.route('/api/sidebar-proyecto')
@login_required
def get_sidebar_proyecto():
    try:
        html = get_menu_proyecto_html(
            session.get('proyecto_actual', PROYECTO_DEFAULT),
            session.get('rol', 'Supervisor'),
            session.get('notif_count', 0),
            request.args.get('endpoint', '')
        )
        return html
    except Exception as e:
        import traceback
        print(f"ERROR en get_sidebar_proyecto: {traceback.format_exc()}")
        return f'<div class="error">Error: {str(e)}</div>', 500


@proyectos_bp.route('/api/proyectos-disponibles')
@login_required
def get_proyectos_disponibles():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT idproyecto, nombre, descripcion FROM tbl_proyecto WHERE activo = 1 ORDER BY nombre")
        rows = cur.fetchall() or []
        cur.close()
        proyecto_actual = session.get('proyecto_actual', 1)
        return jsonify({
            'success': True,
            'proyectos': [{
                'id':          p['idproyecto'],
                'nombre':      p['nombre'],
                'descripcion': p.get('descripcion', ''),
                'activo':      p['idproyecto'] == proyecto_actual,
                'icono':       '📁',
            } for p in rows],
            'proyecto_actual': proyecto_actual
        })
    except Exception:
        proyecto_actual = session.get('proyecto_actual', 1)
        return jsonify({
            'success': True,
            'proyectos': [{'id': 1, 'nombre': 'Desvíos Ambientales',
                           'descripcion': '', 'activo': True, 'icono': '📁'}],
            'proyecto_actual': proyecto_actual
        })
