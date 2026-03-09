from flask import Blueprint, jsonify, session
from extensions import mysql
from utils.helpers import sp_exec

shared_bp = Blueprint('shared', __name__)

@shared_bp.route('/notificaciones')
def get_notificaciones():
    if 'usuario_rol' not in session:
        return jsonify({'notifs': [], 'count': 0})
    try:
        cur = mysql.connection.cursor()
        notifs = sp_exec(cur, 'SP_Notificaciones', (session['usuario_rol'],))
        cur.close()
        
        cur = mysql.connection.cursor()
        cnt = sp_exec(cur, 'SP_ContarNotificaciones', (session['usuario_rol'],))
        cur.close()

        def serialize(obj):
            out = {}
            for k,v in obj.items():
                out[k] = v.strftime('%Y-%m-%d %H:%M') if hasattr(v,'strftime') else (v if v is not None else '')
            return out

        return jsonify({
            'notifs': [serialize(n) for n in notifs],
            'count':  cnt[0]['total'] if cnt else 0
        })
    except Exception as e:
        return jsonify({'notifs': [], 'count': 0, 'error': str(e)})
