# ============================================================================
# AUTENTICACIÓN — Login
# ============================================================================
from flask import render_template, request, redirect, url_for, session
from extensions import mysql
from utils.helpers import consume_results
from routes.core.auth import auth_bp


def sp_fetchone(cur):
    """Obtiene la primera fila del primer result set y consume todos los result sets."""
    result = None
    try:
        rows = cur.fetchall()
        result = rows[0] if rows else None
    except Exception:
        pass
    
    # Consumir todos los result sets pendientes
    try:
        while cur.nextset():
            try:
                cur.fetchall()
            except:
                pass
    except:
        pass
    
    return result


def cargar_modulos_por_rol(proyecto_id, rol_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT
                m.idmodulo, m.idmodulopadre, m.codigo,
                m.nombre, m.icono, m.url, m.orden
            FROM tbl_proyecto_rol_modulo prm
            JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
            WHERE prm.idproyecto = %s AND prm.idroles = %s AND m.activo = 1
            ORDER BY m.orden
        """, (proyecto_id, rol_id))
        modulos_asignados = cur.fetchall()
        cur.close()

        if not modulos_asignados:
            print(f"[cargar_modulos_por_rol] ⚠️ Rol {rol_id} sin módulos en proyecto {proyecto_id}")
            return []

        # Obtener todos los módulos (padres e hijos) del proyecto 1 (Argos)
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT idmodulo, idmodulopadre, codigo, nombre, icono, url, orden
            FROM tbl_modulo
            WHERE idproyecto = 1 AND activo = 1
            ORDER BY orden
        """)
        todos_modulos = cur.fetchall()
        cur.close()

        # Crear un diccionario de módulos asignados por ID
        modulos_asignados_ids = {m['idmodulo'] for m in modulos_asignados}

        # Agregar los padres de los módulos asignados
        modulos_con_padres = set(modulos_asignados_ids)
        for modulo in modulos_asignados:
            if modulo.get('idmodulopadre'):
                modulos_con_padres.add(modulo['idmodulopadre'])

        # Filtrar solo los módulos asignados y sus padres
        modulos_filtrados = [m for m in todos_modulos if m['idmodulo'] in modulos_con_padres]

        # Separar padres e hijos
        padres = [m for m in modulos_filtrados if m.get('idmodulopadre') is None]
        hijos  = [m for m in modulos_filtrados if m.get('idmodulopadre') is not None]

        resultado = []
        for padre in padres:
            modulo = {
                'idmodulo': padre['idmodulo'], 'codigo': padre['codigo'],
                'nombre':   padre['nombre'],   'icono':  padre.get('icono') or 'circle',
                'url':      padre.get('url'),  'orden':  padre.get('orden', 0),
                'hijos':    []
            }
            for hijo in hijos:
                if hijo.get('idmodulopadre') == padre['idmodulo']:
                    modulo['hijos'].append({
                        'idmodulo': hijo['idmodulo'], 'codigo': hijo['codigo'],
                        'nombre':   hijo['nombre'],   'icono':  hijo.get('icono') or 'circle',
                        'url':      hijo.get('url'),  'orden':  hijo.get('orden', 0)
                    })
            modulo['hijos'].sort(key=lambda x: x['orden'])
            resultado.append(modulo)

        resultado.sort(key=lambda x: x['orden'])
        print(f"[cargar_modulos_por_rol] {len(resultado)} módulos padre para rol {rol_id}")
        return resultado

    except Exception as e:
        print(f"[cargar_modulos_por_rol] ERROR: {e}")
        import traceback; traceback.print_exc()
        return []


def set_session(user):
    session['user_id']         = user.get('idusuario')
    session['usuario_rol']     = user.get('idusuariorol')
    session['dni']             = user.get('idusuario')
    session['nombre']          = user.get('nombrecompleto')
    session['rol']             = user.get('nombrerol')
    session['rol_id']          = user.get('idroles')
    session['area_id']         = user.get('idarea')
    session['area_nombre']     = user.get('area_nombre')
    session['cargo']           = user.get('cargo')
    session['proyecto_id']     = user.get('idproyecto')
    session['proyecto_nombre'] = user.get('nombreproyecto')
    session['proyecto_actual'] = 'DESVIOS_AMB'

    modulos = cargar_modulos_por_rol(user.get('idproyecto'), user.get('idroles'))
    if modulos:
        session['modulos'] = modulos
        accesos = [m['codigo'] for m in modulos]
        accesos += [h['codigo'] for m in modulos for h in m.get('hijos', [])]
        session['accesos'] = accesos
        print(f"[set_session] {user.get('nombrerol')} -> {len(accesos)} accesos")
    else:
        session['modulos'] = []
        session['accesos'] = []
    
    # Marcar la sesión como modificada y permanente para asegurar que se guarde
    session.permanent = True
    session.modified = True


def redirect_by_rol(rol):
    if rol == 'Administrador':
        return redirect(url_for('da.dashboard'))
    return redirect(url_for('supervisor.desvios'))


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect_by_rol(session.get('rol'))

    error = None
    if request.method == 'POST':
        dni = request.form.get('dni', '').strip()
        pwd = request.form.get('password', '').strip()

        if not dni or not pwd:
            error = 'DNI y contraseña son requeridos'
        else:
            cur = None
            try:
                cur = mysql.connection.cursor()
                # Usar execute("CALL ...") en lugar de callproc() para mejor compatibilidad
                cur.execute('CALL sp_login(%s, %s)', (dni, pwd))
                user = sp_fetchone(cur)
                cur.close()

                if not user:
                    error = 'DNI o contraseña incorrectos'
                else:
                    cur2 = mysql.connection.cursor()
                    cur2.execute("""
                        SELECT ur.idusuariorol, r.idroles, r.nombrerol,
                               u.idusuario, u.nombrecompleto,
                               ur.idarea, a.nombre AS area_nombre,
                               ur.cargo, ur.idproyecto, p.nombre AS nombreproyecto
                        FROM tbl_usuariorol ur
                        JOIN tbl_roles r ON r.idroles = ur.idroles
                        JOIN tbl_usuario u ON u.idusuario = ur.idusuario
                        LEFT JOIN tbl_area a ON a.idarea = ur.idarea
                        LEFT JOIN tbl_proyecto p ON p.idproyecto = ur.idproyecto
                        WHERE u.idusuario = %s AND u.activo = 1
                    """, (user.get('idusuario'),))
                    roles = cur2.fetchall()
                    cur2.close()

                    if len(roles) > 1:
                        session['_pending_user'] = {
                            'idusuario':      user.get('idusuario'),
                            'nombrecompleto': user.get('nombrecompleto'),
                            'roles': [{
                                'idusuariorol':   r['idusuariorol'],
                                'idroles':        r['idroles'],
                                'nombrerol':      r['nombrerol'],
                                'idarea':         r.get('idarea'),
                                'area_nombre':    r.get('area_nombre'),
                                'cargo':          r.get('cargo'),
                                'idproyecto':     r.get('idproyecto'),
                                'nombreproyecto': r.get('nombreproyecto')
                            } for r in roles]
                        }
                        return redirect(url_for('auth.seleccionar_rol'))
                    else:
                        if roles:
                            for k in ('idusuariorol','idroles','nombrerol','idarea','area_nombre','cargo','idproyecto','nombreproyecto'):
                                user[k] = roles[0].get(k)
                        set_session(user)
                        return redirect_by_rol(user.get('nombrerol'))

            except Exception as e:
                error = f'Error de conexión: {str(e)}'
                print(f"[login] ERROR: {e}")
                import traceback; traceback.print_exc()
            finally:
                if cur:
                    try: cur.close()
                    except Exception: pass

    return render_template('auth/login.html', error=error)
