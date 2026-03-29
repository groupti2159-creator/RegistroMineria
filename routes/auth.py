# ============================================================================
# SISTEMA DE AUTENTICACIÓN CON ROLES PUROS
# ============================================================================
# Sistema basado en tbl_proyecto_rol_modulo (documento TablasAcces - Opción A)
# Los permisos se asignan a ROLES, no a usuarios individuales
# ============================================================================

from flask import Blueprint, render_template, request, redirect, url_for, session
from extensions import mysql
from utils.helpers import consume_results

auth_bp = Blueprint('auth', __name__)

def sp_fetchone(cur):
    """Obtiene el primer resultado de un stored procedure."""
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

def cargar_modulos_por_rol(proyecto_id, rol_id):
    """
    Carga módulos permitidos para un rol en un proyecto.
    Sistema PURO por roles según documento TablasAcces.
    """
    try:
        cur = mysql.connection.cursor()
        
        # Consulta directa a tbl_proyecto_rol_modulo
        cur.execute("""
            SELECT 
                m.idmodulo,
                m.idmodulopadre,
                m.codigo,
                m.nombre,
                m.icono,
                m.url,
                m.orden
            FROM tbl_proyecto_rol_modulo prm
            JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
            WHERE prm.idproyecto = %s 
              AND prm.idroles = %s
              AND m.activo = 1
            ORDER BY m.orden
        """, (proyecto_id, rol_id))
        
        modulos = cur.fetchall()
        cur.close()
        
        if not modulos:
            print(f"[cargar_modulos_por_rol] ⚠️ Rol {rol_id} no tiene módulos en proyecto {proyecto_id}")
            return []
        
        print(f"[cargar_modulos_por_rol] Rol {rol_id} en proyecto {proyecto_id} → {len(modulos)} módulos")
        
        # Separar padres e hijos
        padres = [m for m in modulos if m.get('idmodulopadre') is None]
        hijos = [m for m in modulos if m.get('idmodulopadre') is not None]
        
        # Construir jerarquía
        resultado = []
        for padre in padres:
            modulo = {
                'idmodulo': padre['idmodulo'],
                'codigo': padre['codigo'],
                'nombre': padre['nombre'],
                'icono': padre.get('icono') or 'circle',
                'url': padre.get('url'),
                'orden': padre.get('orden', 0),
                'hijos': []
            }
            
            # Agregar hijos
            for hijo in hijos:
                if hijo.get('idmodulopadre') == padre['idmodulo']:
                    modulo['hijos'].append({
                        'idmodulo': hijo['idmodulo'],
                        'codigo': hijo['codigo'],
                        'nombre': hijo['nombre'],
                        'icono': hijo.get('icono') or 'circle',
                        'url': hijo.get('url'),
                        'orden': hijo.get('orden', 0)
                    })
            
            # Ordenar hijos por orden
            modulo['hijos'].sort(key=lambda x: x['orden'])
            resultado.append(modulo)
        
        # Ordenar padres por orden
        resultado.sort(key=lambda x: x['orden'])
        
        print(f"[cargar_modulos_por_rol] Módulos padre: {[m['codigo'] for m in resultado]}")
        return resultado
        
    except Exception as e:
        print(f"[cargar_modulos_por_rol] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return []

def set_session(user):
    """Configura la sesión del usuario con el sistema de roles puro."""
    usuario_rol_id = user.get('idusuariorol')
    rol_id = user.get('idroles')
    rol_nombre = user.get('nombrerol')
    proyecto_id = user.get('idproyecto')
    
    # Datos básicos de sesión
    session['user_id'] = user.get('idusuario')
    session['usuario_rol'] = usuario_rol_id
    session['dni'] = user.get('idusuario')
    session['nombre'] = user.get('nombrecompleto')
    session['rol'] = rol_nombre
    session['rol_id'] = rol_id
    session['area_id'] = user.get('idarea')
    session['area_nombre'] = user.get('area_nombre')
    session['cargo'] = user.get('cargo')
    session['proyecto_id'] = proyecto_id
    session['proyecto_nombre'] = user.get('nombreproyecto')
    session['proyecto_actual'] = 'DESVIOS_AMB'  # Mantener por compatibilidad
    
    print(f"[set_session] Usuario: {user.get('idusuario')} | Rol: {rol_nombre} | Proyecto: {proyecto_id}")
    
    # Cargar módulos según el rol (sistema puro)
    modulos = cargar_modulos_por_rol(proyecto_id, rol_id)
    
    if modulos:
        session['modulos'] = modulos
        
        # Construir lista de accesos (códigos de módulos)
        accesos = []
        for m in modulos:
            accesos.append(m['codigo'])
            for h in m.get('hijos', []):
                accesos.append(h['codigo'])
        
        session['accesos'] = accesos
        print(f"[set_session] {rol_nombre} → {len(accesos)} módulos cargados")
        print(f"[set_session] Accesos: {accesos}")
    else:
        print(f"[set_session] ❌ ERROR: {rol_nombre} sin módulos asignados")
        session['modulos'] = []
        session['accesos'] = []

def redirect_by_rol(rol):
    """Redirige según el rol del usuario."""
    if rol == 'Administrador':
        return redirect(url_for('da.dashboard'))
    return redirect(url_for('supervisor.desvios'))

@auth_bp.route('/', methods=['GET','POST'])
@auth_bp.route('/login', methods=['GET','POST'])
def login():
    """Login del usuario."""
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
                    # Obtener TODOS los roles/proyectos del usuario
                    cur2 = mysql.connection.cursor()
                    cur2.execute("""
                        SELECT 
                            ur.idusuariorol,
                            r.idroles,
                            r.nombrerol,
                            u.idusuario,
                            u.nombrecompleto,
                            ur.idarea,
                            a.nombre AS area_nombre,
                            ur.cargo,
                            ur.idproyecto,
                            p.nombre AS nombreproyecto
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
                        # Usuario tiene múltiples roles - mostrar selector
                        session['_pending_user'] = {
                            'idusuario': user.get('idusuario'),
                            'nombrecompleto': user.get('nombrecompleto'),
                            'roles': [
                                {
                                    'idusuariorol': r['idusuariorol'],
                                    'idroles': r['idroles'],
                                    'nombrerol': r['nombrerol'],
                                    'idarea': r.get('idarea'),
                                    'area_nombre': r.get('area_nombre'),
                                    'cargo': r.get('cargo'),
                                    'idproyecto': r.get('idproyecto'),
                                    'nombreproyecto': r.get('nombreproyecto')
                                }
                                for r in roles
                            ]
                        }
                        return redirect(url_for('auth.seleccionar_rol'))
                    else:
                        # Un solo rol - login directo
                        # Enriquecer user con datos completos del rol
                        user['idusuariorol'] = roles[0].get('idusuariorol') if roles else None
                        user['idroles'] = roles[0].get('idroles') if roles else None
                        user['nombrerol'] = roles[0].get('nombrerol') if roles else None
                        user['idarea'] = roles[0].get('idarea') if roles else None
                        user['area_nombre'] = roles[0].get('area_nombre') if roles else None
                        user['cargo'] = roles[0].get('cargo') if roles else None
                        user['idproyecto'] = roles[0].get('idproyecto') if roles else None
                        user['nombreproyecto'] = roles[0].get('nombreproyecto') if roles else None
                        set_session(user)
                        return redirect_by_rol(user.get('nombrerol'))

            except Exception as e:
                error = f'Error de conexión: {str(e)}'
                print(f"[login] ERROR: {e}")
                import traceback
                traceback.print_exc()
            finally:
                if cur:
                    try:
                        cur.close()
                    except:
                        pass

    return render_template('auth/login.html', error=error)

@auth_bp.route('/seleccionar-rol', methods=['GET','POST'])
def seleccionar_rol():
    """Selector de rol cuando el usuario tiene múltiples roles."""
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
            return render_template(
                'auth/seleccionar_rol.html',
                pending=pending,
                error='Selección inválida'
            )
        
        session.pop('_pending_user', None)
        
        # Construir objeto user completo
        user = {
            'idusuario': pending['idusuario'],
            'nombrecompleto': pending['nombrecompleto'],
            'idusuariorol': rol_elegido['idusuariorol'],
            'idroles': rol_elegido['idroles'],
            'nombrerol': rol_elegido['nombrerol'],
            'idarea': rol_elegido.get('idarea'),
            'area_nombre': rol_elegido.get('area_nombre'),
            'cargo': rol_elegido.get('cargo'),
            'idproyecto': rol_elegido.get('idproyecto'),
            'nombreproyecto': rol_elegido.get('nombreproyecto')
        }
        
        set_session(user)
        return redirect_by_rol(rol_elegido['nombrerol'])

    return render_template('auth/seleccionar_rol.html', pending=pending)

@auth_bp.route('/logout')
def logout():
    """Cierra la sesión del usuario."""
    session.clear()
    return redirect(url_for('auth.login'))


# ============================================================================
# CÓDIGO ANTIGUO (COMENTADO - SISTEMA CON MÓDULOS PERSONALIZADOS)
# ============================================================================
# Este código usaba tbl_usuario_modulo_personalizado (ya eliminada)
# Se mantiene comentado como referencia histórica
# ============================================================================

# def sp_fetchall(cur):
#     result = []
#     first = True
#     while True:
#         try:
#             rows = cur.fetchall()
#             if first and rows:
#                 result = rows
#                 first = False
#         except Exception:
#             pass
#         if not cur.nextset():
#             break
#     return result

# def cargar_todos_modulos(proyecto_id):
#     """Carga TODOS los módulos de un proyecto (para Administrador)."""
#     try:
#         cur = mysql.connection.cursor()
#         cur.execute("""
#             SELECT m.idmodulo, m.idmodulopadre, m.codigo, m.nombre, m.icono, m.url, m.orden
#             FROM tbl_modulo m
#             WHERE m.idproyecto = %s AND m.activo = 1
#             ORDER BY m.orden
#         """, (proyecto_id,))
#         modulos = cur.fetchall()
#         cur.close()
#         # ... resto del código
#         return []

# def cargar_modulos(usuario_rol_id):
#     """Carga módulos personalizados del usuario desde Tbl_Usuario_Modulo_Personalizado."""
#     # OBSOLETO - tabla eliminada
#     return []
