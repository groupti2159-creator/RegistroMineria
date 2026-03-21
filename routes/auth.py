from flask import Blueprint, render_template, request, redirect, url_for, session
from extensions import mysql
from utils.helpers import consume_results

auth_bp = Blueprint('auth', __name__)

def sp_fetchone(cur):
    result = None
    first = True
    while True:
        try:
            rows = cur.fetchall()
            if first and rows:
                result = rows[0]
                first = False
        except Exception:
            pass
        if not cur.nextset():
            break
    return result

def sp_fetchall(cur):
    result = []
    first = True
    while True:
        try:
            rows = cur.fetchall()
            if first and rows:
                result = rows
                first = False
        except Exception:
            pass
        if not cur.nextset():
            break
    return result

def set_session(user):
    session['user_id']        = user.get('idusuario')
    session['usuario_rol']    = user.get('idusuariorol')
    session['dni']            = user.get('idusuario')  # idusuario ahora ES el dni
    session['nombre']         = user.get('nombrecompleto')
    session['rol']            = user.get('nombrerol')
    session['rol_id']         = user.get('idroles')
    session['proyecto_actual'] = 'DESVIOS_AMB'

def redirect_by_rol(rol):
    if rol == 'Administrador':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('supervisor.desvios'))

@auth_bp.route('/', methods=['GET','POST'])
@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        return redirect_by_rol(session.get('rol'))

    error = None
    if request.method == 'POST':
        dni = request.form.get('dni','').strip()
        pwd = request.form.get('password','').strip()
        if not dni or not pwd:
            error = 'DNI y contraseña son requeridos'
        else:
            cur = None
            try:
                cur = mysql.connection.cursor()
                consume_results(cur)
                cur.callproc('sp_login', (dni, pwd))
                user = sp_fetchone(cur)
                cur.close()

                if not user:
                    error = 'DNI o contraseña incorrectos'
                else:
                    # Obtener TODOS los roles del usuario
                    cur2 = mysql.connection.cursor()
                    cur2.execute("""
                        SELECT ur.idusuariorol, r.idroles, r.nombrerol,
                               u.idusuario, u.nombrecompleto
                        FROM tbl_usuariorol ur
                        JOIN tbl_roles r ON r.idroles = ur.idroles
                        JOIN tbl_usuario u ON u.idusuario = ur.idusuario
                        WHERE u.idusuario = %s AND u.activo = 1
                    """, (user.get('idusuario'),))
                    roles = cur2.fetchall()
                    cur2.close()

                    if len(roles) > 1:
                        session['_pending_user'] = {
                            'idusuario':      user.get('idusuario'),
                            'nombrecompleto': user.get('nombrecompleto'),
                            'roles': [
                                {'idusuariorol': r['idusuariorol'],
                                 'idroles':      r['idroles'],
                                 'nombrerol':    r['nombrerol']}
                                for r in roles
                            ]
                        }
                        return redirect(url_for('auth.seleccionar_rol'))
                    else:
                        set_session(user)
                        return redirect_by_rol(user.get('nombrerol'))

            except Exception as e:
                error = f'Error de conexión: {str(e)}'
                print(f"Login error: {e}")
            finally:
                if cur:
                    try: cur.close()
                    except: pass

    return render_template('auth/login.html', error=error)


@auth_bp.route('/seleccionar-rol', methods=['GET','POST'])
def seleccionar_rol():
    pending = session.get('_pending_user')
    if not pending:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        idusuariorol_raw = request.form.get('idusuariorol')
        # idusuariorol ahora es INT — comparar con cast
        try:
            idusuariorol_int = int(idusuariorol_raw)
        except (TypeError, ValueError):
            idusuariorol_int = None
        rol_elegido = next((r for r in pending['roles'] if r['idusuariorol'] == idusuariorol_int), None)
        if not rol_elegido:
            return render_template('auth/seleccionar_rol.html', pending=pending,
                                   error='Selección inválida')
        session.pop('_pending_user', None)
        session['user_id']        = pending['idusuario']
        session['usuario_rol']    = rol_elegido['idusuariorol']
        session['dni']            = pending['idusuario']  # idusuario ahora ES el dni
        session['nombre']         = pending['nombrecompleto']
        session['rol']            = rol_elegido['nombrerol']
        session['rol_id']         = rol_elegido['idroles']
        session['proyecto_actual'] = 'DESVIOS_AMB'
        return redirect_by_rol(rol_elegido['nombrerol'])

    return render_template('auth/seleccionar_rol.html', pending=pending)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
