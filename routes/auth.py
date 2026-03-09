from flask import Blueprint, render_template, request, redirect, url_for, session
from extensions import mysql
from utils.helpers import consume_results

auth_bp = Blueprint('auth', __name__)

def sp_fetchone(cur):
    """Consume todos los result sets de un callproc y retorna el primero."""
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

@auth_bp.route('/', methods=['GET','POST'])
@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        if session.get('rol') == 'Administrador':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('supervisor.desvios'))

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
                cur.callproc('SP_Login', (dni, pwd))
                user = sp_fetchone(cur)

                if user:
                    session['user_id']     = user.get('idUsuario')
                    session['usuario_rol'] = user.get('IdUsuarioRol')
                    session['dni']         = user.get('DNI')
                    session['nombre']      = user.get('NombreCompleto')
                    session['rol']         = user.get('NombreRol')
                    session['rol_id']      = user.get('idRoles')
                    
                    cur.close()
                    
                    if user.get('NombreRol') == 'Administrador':
                        return redirect(url_for('admin.dashboard'))
                    return redirect(url_for('supervisor.desvios'))
                else:
                    error = 'DNI o contraseña incorrectos'
            except Exception as e:
                error = f'Error de conexión: {str(e)}'
                print(f"Login error: {e}")  # Para debugging
            finally:
                if cur:
                    try:
                        cur.close()
                    except:
                        pass

    return render_template('auth/login.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
