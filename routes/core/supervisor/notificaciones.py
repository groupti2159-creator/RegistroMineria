from flask import session, jsonify, redirect, url_for
from functools import wraps
from extensions import mysql
from utils.helpers import sp_exec
from routes.core.supervisor import supervisor_bp


def sup_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session or session.get('rol') not in ('Supervisor', 'Trabajador'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


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
