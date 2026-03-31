// ============================================================================
// GESTIÓN DE USUARIOS - LÓGICA DE TABLA Y MODALES
// ============================================================================

let proyectosAgregados = [];
let usuarioEditando = null;

/**
 * Abre el modal para crear un nuevo usuario
 */
window.abrirModalCrear = function() {
    usuarioEditando = null;
    const modal = document.getElementById('modalCrearUsuario');
    if (!modal) return;

    modal.classList.add('open');
    proyectosAgregados = [];
    
    document.getElementById('formCrearUsuario').reset();
    document.getElementById('proyectos-container').innerHTML = '';
    document.getElementById('modalTitle').innerHTML = '<i data-feather="user-plus"></i> Crear Nuevo Usuario';
    document.getElementById('guardarUsuarioBtn').textContent = 'Crear Usuario';
    document.getElementById('dni').disabled = false;
    document.getElementById('activo').value = '1';
    
    if (document.getElementById('pswHint')) document.getElementById('pswHint').style.display = 'none';

    agregarProyecto(); // Iniciar con una fila de proyecto
    if (typeof feather !== 'undefined') feather.replace({ 'stroke-width': 1.2 });
};

/**
 * Abre el modal para editar un usuario existente
 */
window.abrirModalEditar = async function(dni) {
    try {
        const response = await fetch(`/admin/usuarios/detalle/${encodeURIComponent(dni)}`);
        const data = await response.json();
        if (!data.success) throw new Error(data.error);

        const u = data.usuario;
        usuarioEditando = dni;

        const modal = document.getElementById('modalCrearUsuario');
        modal.classList.add('open');
        proyectosAgregados = [];
        document.getElementById('formCrearUsuario').reset();
        document.getElementById('proyectos-container').innerHTML = '';
        document.getElementById('modalTitle').innerHTML = '<i data-feather="edit"></i> Editar Usuario';
        document.getElementById('guardarUsuarioBtn').textContent = 'Guardar Cambios';
        
        document.getElementById('dni').value = u.idusuario;
        document.getElementById('dni').disabled = true;
        document.getElementById('nombre').value = u.nombrecompleto;
        document.getElementById('correo').value = u.correo || '';
        document.getElementById('password').value = '';
        document.getElementById('activo').value = u.activo ? '1' : '0';
        
        if (document.getElementById('pswHint')) document.getElementById('pswHint').style.display = 'block';

        if (Array.isArray(data.asignaciones) && data.asignaciones.length) {
            for (const asig of data.asignaciones) {
                await agregarProyecto({
                    proyecto_id: asig.idproyecto,
                    rol_id: asig.idroles,
                    area_id: asig.idarea,
                    cargo: asig.cargo || '',
                    idusuariorol: asig.idusuariorol
                });
            }
        } else {
            agregarProyecto();
        }

        if (typeof feather !== 'undefined') feather.replace({ 'stroke-width': 1.2 });
    } catch (err) {
        mostrarNotificacion(err.message, 'error');
    }
};

/**
 * Cierra el modal de creación/edición
 */
window.cerrarModal = function() {
    document.getElementById('modalCrearUsuario').classList.remove('open');
};

/**
 * Agrega una fila de proyecto al formulario del modal
 */
window.agregarProyecto = function(asignacion = null) {
    const container = document.getElementById('proyectos-container');
    const index = proyectosAgregados.length;
    
    const div = document.createElement('div');
    div.className = 'proyecto-item';
    div.dataset.index = index;
    div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <span style="font-weight: 700; font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase;">Asignación ${index + 1}</span>
            <button type="button" class="btn-icon btn-icon-danger" onclick="eliminarFilaProyecto(${index})">
                <i data-feather="trash-2"></i>
            </button>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Proyecto</label>
                <select id="proyecto_${index}" class="form-select" required></select>
            </div>
            <div class="form-group">
                <label class="form-label">Rol</label>
                <select id="rol_${index}" class="form-select" required></select>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Área</label>
                <select id="area_${index}" class="form-select" required></select>
            </div>
            <div class="form-group">
                <label class="form-label">Cargo</label>
                <input type="text" id="cargo_${index}" class="form-input" placeholder="Ej: Jefe de SSHO" required>
            </div>
        </div>
        <input type="hidden" id="idusuariorol_${index}" value="${asignacion ? asignacion.idusuariorol : ''}">
    `;
    
    container.appendChild(div);
    proyectosAgregados.push({});
    
    const p1 = cargarCombo('/admin/roles/proyectos', `proyecto_${index}`, 'idproyecto', 'nombre', asignacion?.proyecto_id);
    const p2 = cargarCombo('/admin/usuarios/roles', `rol_${index}`, 'idroles', 'nombrerol', asignacion?.rol_id);
    const p3 = cargarCombo('/admin/usuarios/areas', `area_${index}`, 'idarea', 'nombrearea', asignacion?.area_id);
    
    if (asignacion?.cargo) document.getElementById(`cargo_${index}`).value = asignacion.cargo;
    
    if (typeof feather !== 'undefined') feather.replace({ 'stroke-width': 1.2 });
    return Promise.all([p1, p2, p3]);
};

async function cargarCombo(url, elementId, valKey, textKey, selectedValue) {
    const res = await fetch(url);
    const data = await res.json();
    const select = document.getElementById(elementId);
    if (!select) return;

    const items = data.proyectos || data; 
    
    select.innerHTML = '<option value="">Seleccionar...</option>';
    items.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item[valKey];
        opt.textContent = item[textKey];
        if (selectedValue && item[valKey] == selectedValue) opt.selected = true;
        select.appendChild(opt);
    });
}

window.eliminarFilaProyecto = function(index) {
    const el = document.querySelector(`.proyecto-item[data-index="${index}"]`);
    if (el) el.remove();
};

/**
 * Acción de guardar (crear o actualizar) un usuario
 */
window.guardarUsuario = async function() {
    const btn = document.getElementById('guardarUsuarioBtn');
    btn.disabled = true;
    
    try {
        const payload = {
            nombre: document.getElementById('nombre').value.trim(),
            correo: document.getElementById('correo').value.trim(),
            password: document.getElementById('password').value.trim(),
            activo: parseInt(document.getElementById('activo').value),
            asignaciones: []
        };

        if (!usuarioEditando) payload.dni = document.getElementById('dni').value.trim();

        // Recopilar asignaciones
        const rows = document.querySelectorAll('.proyecto-item');
        rows.forEach(row => {
            const idx = row.dataset.index;
            payload.asignaciones.push({
                idusuariorol: document.getElementById(`idusuariorol_${idx}`).value || null,
                proyecto_id: document.getElementById(`proyecto_${idx}`).value,
                rol_id: document.getElementById(`rol_${idx}`).value,
                area_id: document.getElementById(`area_${idx}`).value,
                cargo: document.getElementById(`cargo_${idx}`).value.trim()
            });
        });

        // Validaciones básicas
        if (!payload.nombre || payload.asignaciones.length === 0) {
            throw new Error("Completa el nombre y al menos una asignación de proyecto.");
        }

        const url = usuarioEditando ? `/admin/usuarios/editar/${usuarioEditando}` : '/admin/usuarios/crear-nuevo';
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await res.json();
        if (!result.success) throw new Error(result.error);

        mostrarNotificacion(usuarioEditando ? 'Usuario actualizado' : 'Usuario creado', 'success');
        cerrarModal();
        location.reload();
    } catch (e) {
        mostrarNotificacion(e.message, 'error');
    } finally {
        btn.disabled = false;
    }
};

// ============================================================================
// HELPERS & ACCIONES DE TABLA
// ============================================================================

if (typeof window.mostrarNotificacion !== 'function') {
    window.mostrarNotificacion = function (mensaje, tipo = 'success') {
        const notif = document.createElement('div');
        notif.className = 'ajax-notificacion notif-' + tipo;
        notif.style.cssText = `
            position: fixed; top: 20px; right: 20px; z-index: 10000;
            padding: 1rem 1.5rem; border-radius: 8px; color: white;
            background: ${tipo === 'success' ? '#10b981' : '#ef4444'};
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        `;
        notif.innerHTML = `<span>${mensaje}</span>`;
        document.body.appendChild(notif);
        setTimeout(() => notif.remove(), 3000);
    };
}

window.eliminarUsuarioFisico = async function(dni) {
    if (!confirm('¡PELIGRO! ¿Desea eliminar permanentemente este usuario? Esta acción es irreversible.')) return;
    try {
        const res = await fetch(`/admin/usuarios/eliminar-fisico/${dni}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            mostrarNotificacion('Usuario eliminado correctamente', 'success');
            location.reload();
        } else {
            throw new Error(data.error);
        }
    } catch (e) {
        mostrarNotificacion(e.message, 'error');
    }
};