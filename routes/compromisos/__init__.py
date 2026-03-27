from flask import Blueprint, redirect, url_for, session
from functools import wraps

compromisos_bp = Blueprint('compromisos', __name__)

def _login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

from routes.compromisos import dashboard, registro, exportar