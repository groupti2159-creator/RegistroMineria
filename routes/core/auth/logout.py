from flask import session, redirect, url_for
from routes.core.auth import auth_bp


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
