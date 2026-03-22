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

def _query_modulos(rol_id):
    """Query base que obtiene módulos del rol desde la BD."""
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DISTINCT m.idmodulo, m.codigo, m.nombre, m.icono, m.url, m.orden
        FROM tbl_modulo m
        JOIN tbl_modulo_permiso mp ON mp.idmodulo = m.idmodulo
        WHERE mp.idroles = %s AND m.activo = 1
        ORDER BY m.orden ASC
    """, (rol_id,))
    rows = cur.fetchall()
    cur.close()
    return rows

def cargar_accesos(rol_id, area_id=None):
    """Retorna lista de códigos de módulos permitidos para el rol."""
    try:
        return [r['codigo'] for r in _query_modulos(rol_id)]
    except Exception as e:
        print(f"[cargar_accesos] error: {e}")
        return []

def cargar_modulos(rol_id):
    """Retorna lista de módulos completos para construir el sidebar dinámicamente."""
    try:
        rows = _query_modulos(rol_id)
        print(f"[cargar_modulos] rol_id={rol_id} → {len(rows)} módulos: {[(r['codigo'], r['orden'], r['url']) for r in rows]}")

        # Separar grupos padre (sin url) e items con url
        grupos_padre = [r for r in rows if not r['url']]
        items_con_url = [r for r in rows if r['url']]

        # Ordenar grupos por orden para calcular rangos
        grupos_padre_sorted = sorted(grupos_padre, key=lambda r: r['orden'])

        # Calcular rango de cada grupo: (orden_grupo, orden_siguiente_grupo)
        # Un hijo pertenece al grupo si su orden > orden_grupo y < orden_siguiente_grupo.
        # Si no hay siguiente grupo, el rango termina en orden_grupo + 10
        # (convención: grupos en múltiplos de 10, hijos en +1..+9)
        rangos = []
        for i, g in enumerate(grupos_padre_sorted):
            orden_inicio = g['orden']
            if i + 1 < len(grupos_padre_sorted):
                orden_fin = grupos_padre_sorted[i + 1]['orden']
            else:
                orden_fin = orden_inicio + 10  # máximo 9 hijos por grupo
            rangos.append((orden_inicio, orden_fin, g))

        def find_padre(orden_item):
            """Retorna el dict del grupo padre si el item cae en su rango, sino None."""
            for o_ini, o_fin, g in rangos:
                if o_ini < orden_item < o_fin:
                    return g
            return None

        # Construir estructura final manteniendo orden
        grupos_map = {}  # codigo -> dict con hijos
        modulos = []

        for r in rows:
            m = {
                'idmodulo': r['idmodulo'],
                'codigo':   r['codigo'],
                'nombre':   r['nombre'],
                'icono':    r['icono'] or 'circle',
                'url':      r['url'],
                'orden':    r['orden'],
                'hijos':    [],
            }
            if not r['url']:
                # Grupo padre
                grupos_map[r['codigo']] = m
                modulos.append(m)
            else:
                padre = find_padre(r['orden'])
                if padre and padre['codigo'] in grupos_map:
                    grupos_map[padre['codigo']]['hijos'].append(m)
                else:
                    modulos.append(m)

        print(f"[cargar_modulos] sidebar final: {[m['codigo'] for m in modulos]}")
        return modulos
    except Exception as e:
        print(f"[cargar_modulos] error: {e}")
        import traceback; traceback.print_exc()
        return []

def set_session(user):
    rol_id  = user.get('idroles')
    area_id = user.get('idarea')
    session['user_id']        = user.get('idusuario')
    session['usuario_rol']    = user.get('idusuariorol')
    session['dni']            = user.get('idusuario')
    session['nombre']         = user.get('nombrecompleto')
    session['rol']            = user.get('nombrerol')
    session['rol_id']         = rol_id
    session['area_id']        = area_id
    session['cargo']          = user.get('cargo')
    session['proyecto_actual'] = 'DESVIOS_AMB'
    session['accesos']        = cargar_accesos(rol_id, area_id)
    session['modulos']        = cargar_modulos(rol_id)

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
                               u.idusuario, u.nombrecompleto,
                               ur.idarea, ur.cargo
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
                                 'nombrerol':    r['nombrerol'],
                                 'idarea':       r.get('idarea'),
                                 'cargo':        r.get('cargo')}
                                for r in roles
                            ]
                        }
                        return redirect(url_for('auth.seleccionar_rol'))
                    else:
                        # Un solo rol — enriquecer user con idarea y cargo
                        user['idarea'] = roles[0].get('idarea') if roles else None
                        user['cargo']  = roles[0].get('cargo')  if roles else None
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
        session['dni']            = pending['idusuario']
        session['nombre']         = pending['nombrecompleto']
        session['rol']            = rol_elegido['nombrerol']
        session['rol_id']         = rol_elegido['idroles']
        session['area_id']        = rol_elegido.get('idarea')
        session['cargo']          = rol_elegido.get('cargo')
        session['proyecto_actual'] = 'DESVIOS_AMB'
        session['accesos']        = cargar_accesos(rol_elegido['idroles'], rol_elegido.get('idarea'))
        session['modulos']        = cargar_modulos(rol_elegido['idroles'])
        return redirect_by_rol(rol_elegido['nombrerol'])

    return render_template('auth/seleccionar_rol.html', pending=pending)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
