from flask import render_template, request, redirect, url_for, session
from routes.core.auth import auth_bp
from routes.core.auth.login import set_session, redirect_by_rol


@auth_bp.route('/seleccionar-rol', methods=['GET', 'POST'])
def seleccionar_rol():
    pending = session.get('_pending_user')
    if not pending:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        idusuariorol_raw = request.form.get('idusuariorol')
        try:
            idusuariorol_int = int(idusuariorol_raw)
        except (TypeError, ValueError):
            idusuariorol_int = None

        rol_elegido = next(
            (r for r in pending['roles'] if r['idusuariorol'] == idusuariorol_int),
            None
        )

        if not rol_elegido:
            return render_template('auth/seleccionar_rol.html', pending=pending, error='Selección inválida')

        session.pop('_pending_user', None)

        user = {
            'idusuario':      pending['idusuario'],
            'nombrecompleto': pending['nombrecompleto'],
            'idusuariorol':   rol_elegido['idusuariorol'],
            'idroles':        rol_elegido['idroles'],
            'nombrerol':      rol_elegido['nombrerol'],
            'idarea':         rol_elegido.get('idarea'),
            'area_nombre':    rol_elegido.get('area_nombre'),
            'cargo':          rol_elegido.get('cargo'),
            'idproyecto':     rol_elegido.get('idproyecto'),
            'nombreproyecto': rol_elegido.get('nombreproyecto')
        }

        set_session(user)
        return redirect_by_rol(rol_elegido['nombrerol'])

    return render_template('auth/seleccionar_rol.html', pending=pending)
