"""API para obtener personal por área"""
from flask import jsonify
from routes.desvios_ambientales import da_bp
from extensions import mysql
from utils.helpers import sp_exec


@da_bp.route('/api/personal-por-area/<int:id_area>', methods=['GET'])
def obtener_personal_por_area(id_area):
    """Obtiene el personal de un área reportante específica."""
    try:
        cur = mysql.connection.cursor()
        personal = sp_exec(cur, 'sp_obtener_personal_por_area', (id_area,))
        cur.close()
        return jsonify({'success': True, 'personal': personal})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@da_bp.route('/api/todo-personal', methods=['GET'])
def obtener_todo_personal():
    """Obtiene todo el personal activo (para selector de personal responsable)."""
    try:
        cur = mysql.connection.cursor()
        personal = sp_exec(cur, 'sp_obtener_todo_personal')
        cur.close()
        return jsonify({'success': True, 'personal': personal})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@da_bp.route('/api/riesgos-criticos-por-tipo/<int:id_tipo>', methods=['GET'])
def obtener_riesgos_criticos_por_tipo(id_tipo):
    """Obtiene los riesgos críticos según el tipo (1=SEGURIDAD, 2=MEDIO AMBIENTE)."""
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, codigo, descripcion, tipo_asociado
            FROM tbl_riesgos_criticos
            WHERE tipo_asociado = %s AND activo = 1
            ORDER BY codigo ASC
        """, (id_tipo,))
        riesgos = cur.fetchall()
        cur.close()
        return jsonify({'success': True, 'riesgos': riesgos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
