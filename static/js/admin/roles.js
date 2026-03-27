// Variables globales
let proyectoActual = null;
let modulosProyecto = [];
let rolesProyecto = [];

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    cargarProyectos();
    
    // Event listener para cambio de proyecto
    document.getElementById('proyectoSelect').addEventListener('change', function() {
        proyectoActual = this.value;
        if (proyectoActual) {
            cargarRolesYModulos(proyectoActual);
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
async function cargarRolesYModulos(proyectoId) {
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
        rolesProyecto = rolesData.roles;
        
        // Cargar módulos
        const modulosResponse = await fetch(`/admin/roles/proyecto/${proyectoId}/modulos`);
        const modulosData = await modulosResponse.json();
        modulosProyecto = modulosData.modulos;
        
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
}

// Renderizar tarjetas de roles
function renderizarRoles() {
    const container = document.getElementById('rolesContainer');
    
    if (rolesProyecto.length === 0) {
        container.innerHTML = `
            <div class="alert alert-info">
                <i data-feather="info"></i>
                No hay roles configurados para este proyecto. Crea uno nuevo.
            </div>
        `;
        feather.replace();
        return;
    }
    
    container.innerHTML = '';
    
    rolesProyecto.forEach(rol => {
        const card = crearTarjetaRol(rol);
        container.appendChild(card);
    });
    
    feather.replace();
}

// Crear tarjeta de rol
function crearTarjetaRol(rol) {
    const div = document.createElement('div');
    div.className = 'role-card';
    div.dataset.rolId = rol.idroles;
    
    // Contar módulos asignados
    const modulosAsignados = rol.modulos_asignados || 0;
    const totalModulos = modulosProyecto.reduce((acc, grupo) => acc + 1 + grupo.hijos.length, 0);
    
    div.innerHTML = `
        <div class="role-header">
            <div>
                <div class="role-name">
                    <i data-feather="shield"></i>
                    ${rol.nombrerol}
                </div>
                <div class="role-description">${rol.descripcion || 'Sin descripción'}</div>
            </div>
            <div>
                <span class="stats-badge">
                    ${modulosAsignados} / ${totalModulos} módulos
                </span>
            </div>
        </div>
        
        <div class="modulos-tree" id="modulos-rol-${rol.idroles}">
            ${construirArbolModulos(rol)}
        </div>
        
        <div class="text-right mt-3">
            <button class="btn btn-save-role" onclick="guardarPermisosRol(${rol.idroles})">
                <i data-feather="save"></i> Guardar Cambios
            </button>
        </div>
    `;
    
    return div;
}

// Construir árbol de módulos con checkboxes
function construirArbolModulos(rol) {
    let html = '';
    
    modulosProyecto.forEach(grupo => {
        const grupoChecked = rol.modulos_ids && rol.modulos_ids.includes(grupo.idmodulo);
        
        html += `
            <div class="modulo-grupo-item">
                <label>
                    <input type="checkbox" 
                           class="grupo-checkbox" 
                           data-rol="${rol.idroles}"
                           data-grupo="${grupo.idmodulo}"
                           ${grupoChecked ? 'checked' : ''}
                           onchange="toggleGrupoCompleto(this)">
                    <i data-feather="${grupo.icono || 'folder'}" style="width: 18px; height: 18px;"></i>
                    ${grupo.nombre}
                </label>
                
                <div class="modulo-hijos-list">
        `;
        
        grupo.hijos.forEach(hijo => {
            const hijoChecked = rol.modulos_ids && rol.modulos_ids.includes(hijo.idmodulo);
            
            html += `
                <label>
                    <input type="checkbox" 
                           class="hijo-checkbox" 
                           data-rol="${rol.idroles}"
                           data-grupo="${grupo.idmodulo}"
                           data-modulo="${hijo.idmodulo}"
                           ${hijoChecked ? 'checked' : ''}
                           onchange="checkGrupoPadre(this)">
                    <i data-feather="${hijo.icono || 'circle'}" style="width: 14px; height: 14px;"></i>
                    ${hijo.nombre}
                </label>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    return html;
}

// Toggle grupo completo (marcar/desmarcar todos los hijos)
function toggleGrupoCompleto(checkbox) {
    const rolId = checkbox.dataset.rol;
    const grupoId = checkbox.dataset.grupo;
    const checked = checkbox.checked;
    
    const container = document.getElementById(`modulos-rol-${rolId}`);
    const hijos = container.querySelectorAll(`.hijo-checkbox[data-grupo="${grupoId}"]`);
    
    hijos.forEach(hijo => {
        hijo.checked = checked;
    });
}

// Verificar si todos los hijos están marcados para marcar el padre
function checkGrupoPadre(checkbox) {
    const rolId = checkbox.dataset.rol;
    const grupoId = checkbox.dataset.grupo;
    
    const container = document.getElementById(`modulos-rol-${rolId}`);
    const hijos = container.querySelectorAll(`.hijo-checkbox[data-grupo="${grupoId}"]`);
    const todosChecked = Array.from(hijos).every(h => h.checked);
    const algunoChecked = Array.from(hijos).some(h => h.checked);
    
    const grupoPadre = container.querySelector(`.grupo-checkbox[data-grupo="${grupoId}"]`);
    if (grupoPadre) {
        grupoPadre.checked = todosChecked;
        // Opcional: agregar estado indeterminado si algunos están marcados
        grupoPadre.indeterminate = algunoChecked && !todosChecked;
    }
}

// Guardar permisos de un rol
async function guardarPermisosRol(rolId) {
    try {
        const container = document.getElementById(`modulos-rol-${rolId}`);
        
        // Recopilar todos los módulos marcados (grupos + hijos)
        const modulosSeleccionados = [];
        
        // Grupos marcados
        container.querySelectorAll('.grupo-checkbox:checked').forEach(check => {
            modulosSeleccionados.push(parseInt(check.dataset.grupo));
        });
        
        // Hijos marcados
        container.querySelectorAll('.hijo-checkbox:checked').forEach(check => {
            modulosSeleccionados.push(parseInt(check.dataset.modulo));
        });
        
        // Enviar al servidor
        const response = await fetch(`/admin/roles/proyecto/${proyectoActual}/rol/${rolId}/permisos`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                modulos: modulosSeleccionados
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Mostrar mensaje de éxito
            mostrarNotificacion('Permisos guardados correctamente', 'success');
            
            // Recargar datos para actualizar contadores
            await cargarRolesYModulos(proyectoActual);
        } else {
            mostrarNotificacion('Error: ' + result.error, 'error');
        }
        
    } catch (error) {
        console.error('Error guardando permisos:', error);
        mostrarNotificacion('Error al guardar permisos', 'error');
    }
}

// Abrir modal para crear nuevo rol
function abrirModalNuevoRol() {
    if (!proyectoActual) {
        alert('Primero selecciona un proyecto');
        return;
    }
    
    document.getElementById('formNuevoRol').reset();
    $('#modalNuevoRol').modal('show');
}

// Crear nuevo rol
async function crearNuevoRol() {
    const nombre = document.getElementById('nuevoRolNombre').value.trim();
    const descripcion = document.getElementById('nuevoRolDescripcion').value.trim();
    
    if (!nombre) {
        alert('El nombre del rol es requerido');
        return;
    }
    
    try {
        const response = await fetch('/admin/roles/crear', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                nombre: nombre,
                descripcion: descripcion
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            $('#modalNuevoRol').modal('hide');
            mostrarNotificacion('Rol creado correctamente', 'success');
            
            // Recargar roles
            await cargarRolesYModulos(proyectoActual);
        } else {
            mostrarNotificacion('Error: ' + result.error, 'error');
        }
        
    } catch (error) {
        console.error('Error creando rol:', error);
        mostrarNotificacion('Error al crear rol', 'error');
    }
}

// Mostrar notificación
function mostrarNotificacion(mensaje, tipo) {
    const alertClass = tipo === 'success' ? 'alert-success' : 'alert-danger';
    const icon = tipo === 'success' ? 'check-circle' : 'alert-circle';
    
    const div = document.createElement('div');
    div.className = `alert ${alertClass} alert-dismissible fade show`;
    div.style.position = 'fixed';
    div.style.top = '20px';
    div.style.right = '20px';
    div.style.zIndex = '9999';
    div.style.minWidth = '300px';
    div.innerHTML = `
        <i data-feather="${icon}"></i>
        ${mensaje}
        <button type="button" class="close" data-dismiss="alert">&times;</button>
    `;
    
    document.body.appendChild(div);
    feather.replace();
    
    setTimeout(() => {
        div.remove();
    }, 3000);
}
