// Variables globales - accesibles desde el HTML
window.proyectoActual = null;
window.modulosProyecto = [];
window.rolesProyecto = [];

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    cargarProyectos();
    
    // Event listener para cambio de proyecto
    document.getElementById('proyectoSelect').addEventListener('change', function() {
        window.proyectoActual = this.value;
        if (window.proyectoActual) {
            cargarRolesYModulos(window.proyectoActual);
        } else {
            document.getElementById('rolesContainer').innerHTML = `
                <div class="text-center text-muted py-5">
                    <i data-feather="folder" style="width: 48px; height: 48px;"></i>
                    <p class="mt-3">Selecciona un proyecto para ver sus roles</p>
                </div>
            `;
            feather.replace();
        }
    });
});

// Cargar lista de proyectos
async function cargarProyectos() {
    try {
        const response = await fetch('/admin/roles/proyectos');
        const data = await response.json();
        
        const select = document.getElementById('proyectoSelect');
        select.innerHTML = '<option value="">Seleccionar proyecto...</option>';
        
        data.proyectos.forEach(p => {
            select.innerHTML += `<option value="${p.idproyecto}">${p.nombre}</option>`;
        });
    } catch (error) {
        console.error('Error cargando proyectos:', error);
        alert('Error al cargar proyectos');
    }
}

// Cargar roles y módulos del proyecto
window.cargarRolesYModulos = async function(proyectoId) {
    try {
        // Mostrar loading
        document.getElementById('rolesContainer').innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Cargando...</span>
                </div>
                <p class="mt-3">Cargando roles y módulos...</p>
            </div>
        `;
        
        // Cargar roles
        const rolesResponse = await fetch(`/admin/roles/proyecto/${proyectoId}/roles`);
        const rolesData = await rolesResponse.json();
        window.rolesProyecto = rolesData.roles;
        
        // Cargar módulos
        const modulosResponse = await fetch(`/admin/roles/proyecto/${proyectoId}/modulos`);
        const modulosData = await modulosResponse.json();
        window.modulosProyecto = modulosData.modulos;
        
        // Renderizar roles
        renderizarRoles();
        
    } catch (error) {
        console.error('Error cargando datos:', error);
        document.getElementById('rolesContainer').innerHTML = `
            <div class="alert alert-danger">
                <i data-feather="alert-circle"></i>
                Error al cargar los datos del proyecto
            </div>
        `;
        feather.replace();
    }
};

// Renderizar tarjetas de roles usando la función del HTML
function renderizarRoles() {
    // Agrupar módulos por categoría para compatibilidad
    const modulosPorCategoria = {};
    
    window.modulosProyecto.forEach(grupo => {
        const categoria = 'Módulos'; // Categoría por defecto
        if (!modulosPorCategoria[categoria]) {
            modulosPorCategoria[categoria] = [];
        }
        
        // Agregar el grupo padre
        modulosPorCategoria[categoria].push({
            id: grupo.idmodulo,
            nombre: grupo.nombre,
            icono: grupo.icono,
            categoria: categoria
        });
        
        // Agregar los hijos
        grupo.hijos.forEach(hijo => {
            modulosPorCategoria[categoria].push({
                id: hijo.idmodulo,
                nombre: hijo.nombre,
                icono: hijo.icono,
                categoria: categoria
            });
        });
    });
    
    // Convertir roles al formato esperado
    const rolesFormateados = window.rolesProyecto.map(rol => ({
        id: rol.idroles,
        nombre: rol.nombrerol,
        descripcion: rol.descripcion,
        es_administrador: false,
        permisos: (rol.modulos_ids || []).reduce((acc, id) => {
            acc[id] = true;
            return acc;
        }, {})
    }));
    
    // Llamar a la función del HTML
    if (typeof window.renderRoles === 'function') {
        window.renderRoles(rolesFormateados, Object.values(modulosPorCategoria).flat());
    }
}

// guardarPermisos vive en roles.html (inline) y solo toma checkboxes del rol indicado.
// No redefinir aquí: antes se hacía querySelectorAll global y se mezclaban permisos de todos los roles.
