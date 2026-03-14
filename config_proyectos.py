"""
Configuración de proyectos y menús dinámicos
"""

# Proyecto por defecto
PROYECTO_DEFAULT = 'DESVIOS_AMB'

def get_menu_proyecto_html(codigo_proyecto, rol, notif_count=0, request_endpoint=''):
    """
    Retorna el HTML completo del sidebar según el proyecto y rol del usuario
    
    Args:
        codigo_proyecto: Código del proyecto actual
        rol: Rol del usuario (Administrador, Supervisor, Trabajador)
        notif_count: Número de notificaciones pendientes
        request_endpoint: Endpoint actual de Flask para marcar items activos
    
    Returns:
        String con HTML del sidebar
    """
    
    # Menú para proyecto DESVIOS_AMB (Desvíos Ambientales)
    if codigo_proyecto == 'DESVIOS_AMB':
        if rol == 'Administrador':
            html = f'''
            <a href="/admin/dashboard" class="nav-item {'active' if request_endpoint == 'admin.dashboard' else ''}">
                <span class="nav-icon"><i data-feather="home"></i></span><span>Dashboard</span>
            </a>
            
            <div class="nav-group">
                <button class="nav-item nav-toggle {'active' if request_endpoint in ['admin.desvios', 'admin.registrar'] else ''}" onclick="toggleSubmenu(this)">
                    <span class="nav-icon"><i data-feather="alert-triangle"></i></span>
                    <span>Desvíos Ambientales</span>
                    {f'<span class="nav-badge">{notif_count}</span>' if notif_count > 0 else ''}
                    <span class="nav-arrow"><i data-feather="chevron-down"></i></span>
                </button>
                <div class="nav-submenu {'open' if request_endpoint in ['admin.desvios', 'admin.registrar'] else ''}">
                    <a href="/admin/registrar" class="nav-subitem {'active' if request_endpoint in ['admin.registrar', 'admin.desvios'] else ''}">
                        <span class="nav-icon"><i data-feather="file-plus"></i></span><span>Registrar Reporte</span>
                    </a>
                </div>
            </div>

            <div class="nav-group">
                <button class="nav-item nav-toggle {'active' if request_endpoint in ['admin.estadisticas_areas', 'admin.estadisticas_ccta', 'admin.estadisticas_tipos', 'admin.estadisticas'] else ''}" onclick="toggleSubmenu(this)">
                    <span class="nav-icon"><i data-feather="bar-chart-2"></i></span>
                    <span>Estadísticas</span>
                    <span class="nav-arrow"><i data-feather="chevron-down"></i></span>
                </button>
                <div class="nav-submenu {'open' if request_endpoint in ['admin.estadisticas_areas', 'admin.estadisticas_ccta', 'admin.estadisticas_tipos', 'admin.estadisticas'] else ''}">
                    <a href="/admin/estadisticas/areas" class="nav-subitem {'active' if request_endpoint == 'admin.estadisticas_areas' else ''}">
                        <span class="nav-icon"><i data-feather="users"></i></span><span>Áreas Responsables</span>
                    </a>
                    <a href="/admin/estadisticas/ccta" class="nav-subitem {'active' if request_endpoint == 'admin.estadisticas_ccta' else ''}">
                        <span class="nav-icon"><i data-feather="user-check"></i></span><span>Ccta Responsables</span>
                    </a>
                    <a href="/admin/estadisticas/tipos" class="nav-subitem {'active' if request_endpoint == 'admin.estadisticas_tipos' else ''}">
                        <span class="nav-icon"><i data-feather="alert-triangle"></i></span><span>Tipos de Desvío</span>
                    </a>
                </div>
            </div>
            
            <div class="nav-group">
                <button class="nav-item nav-toggle {'active' if request_endpoint in ['admin.configuracion', 'admin.configuracion_usuarios'] else ''}" onclick="toggleSubmenu(this)">
                    <span class="nav-icon"><i data-feather="settings"></i></span>
                    <span>Configuración</span>
                    <span class="nav-arrow"><i data-feather="chevron-down"></i></span>
                </button>
                <div class="nav-submenu {'open' if request_endpoint in ['admin.configuracion', 'admin.configuracion_usuarios'] else ''}">
                    <a href="/admin/configuracion/usuarios" class="nav-subitem {'active' if request_endpoint == 'admin.configuracion_usuarios' else ''}">
                        <span class="nav-icon"><i data-feather="users"></i></span><span>Usuarios</span>
                    </a>
                </div>
            </div>
            '''
            return html
        else:  # Supervisor
            html = f'''
            <a href="/supervisor/desvios" class="nav-item {'active' if request_endpoint == 'supervisor.desvios' else ''}">
                <span class="nav-icon"><i data-feather="alert-triangle"></i></span><span>Desvíos Ambientales</span>
                {f'<span class="nav-badge">{notif_count}</span>' if notif_count > 0 else ''}
            </a>
            '''
            return html
    
    # Menú para PROYECTO_B
    elif codigo_proyecto == 'PROYECTO_B':
        html = f'''
        <a href="/proyectos/dashboard/PROYECTO_B" class="nav-item {'active' if request_endpoint == 'proyectos.dashboard_proyecto' else ''}">
            <span class="nav-icon"><i data-feather="home"></i></span><span>Dashboard</span>
        </a>
        <a href="#" class="nav-item disabled">
            <span class="nav-icon"><i data-feather="box"></i></span><span>Módulo 1</span>
        </a>
        <a href="#" class="nav-item disabled">
            <span class="nav-icon"><i data-feather="package"></i></span><span>Módulo 2</span>
        </a>
        <a href="#" class="nav-item disabled">
            <span class="nav-icon"><i data-feather="file-text"></i></span><span>Reportes</span>
        </a>
        '''
        return html
    
    # Menú para PROYECTO_C
    elif codigo_proyecto == 'PROYECTO_C':
        html = f'''
        <a href="/proyectos/dashboard/PROYECTO_C" class="nav-item {'active' if request_endpoint == 'proyectos.dashboard_proyecto' else ''}">
            <span class="nav-icon"><i data-feather="home"></i></span><span>Dashboard</span>
        </a>
        <a href="#" class="nav-item disabled">
            <span class="nav-icon"><i data-feather="calendar"></i></span><span>Planificación</span>
        </a>
        <a href="#" class="nav-item disabled">
            <span class="nav-icon"><i data-feather="briefcase"></i></span><span>Recursos</span>
        </a>
        <a href="#" class="nav-item disabled">
            <span class="nav-icon"><i data-feather="settings"></i></span><span>Configuración</span>
        </a>
        '''
        return html
    
    # Menú por defecto
    return '''
    <a href="/" class="nav-item active">
        <span class="nav-icon"><i data-feather="home"></i></span><span>Dashboard</span>
    </a>
    '''
