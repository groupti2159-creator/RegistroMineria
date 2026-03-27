// Formulario simple de creación de usuarios

let proyectosAgregados = [];

function abrirModalCrear() {
    const modal = document.getElementById('modalCrearUsuario');
    modal.classList.add('open');
    proyectosAgregados = [];
    document.getElementById('formCrearUsuario').reset();
    document.getElementById('proyectos-container').innerHTML = '';
}

function cerrarModal() {
    const modal = document.getElementById('modalCrearUsuario');
    modal.classList.remove('open');
}

function agregarProyecto() {
    const container = document.getElementById('proyectos-container');
    const index = proyectosAgregados.length;
    
    const proyectoDiv = document.createElement('div');
    proyectoDiv.className = 'proyecto-item';
    proyectoDiv.dataset.index = index;
    proyectoDiv.innerHTML = `
        <div class="proyecto-item-header">
            <strong style="color: var(--text); font-size: .95rem;">
                <i data-feather="folder" style="width: 16px; height: 16px; vertical-align: middle; margin-right: .35rem;"></i>
                Proyecto ${index + 1}
            </strong>
            <button type="button" class="btn btn-secondary" style="padding: .45rem .85rem; font-size: .8rem;" onclick="eliminarProyecto(${index})">
                <i data-feather="x" style="width: 14px; height: 14px;"></i>
                Eliminar
            </button>
        </div>
        
        <div class="form-row" style="gap: 1.25rem;">
            <div class="form-group">
                <label class="form-label">PROYECTO *</label>
                <select id="proyecto_${index}" class="form-select" required>
                    <option value="">Seleccionar proyecto...</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">ROL *</label>
                <select id="rol_${index}" class="form-select" required>
                    <option value="">Seleccionar rol...</option>
                </select>
            </div>
        </div>
        
        <div class="form-row" style="gap: 1.25rem;">
            <div class="form-group">
                <label class="form-label">ÁREA *</label>
                <select id="area_${index}" class="form-select" required>
                    <option value="">Seleccionar área...</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">CARGO *</label>
                <input type="text" id="cargo_${index}" class="form-input" placeholder="Ej: Ingeniero Ambiental" required>
            </div>
        </div>
    `;
    
    container.appendChild(proyectoDiv);
    proyectosAgregados.push({});
    
    // Reemplazar iconos de feather
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Cargar datos
    cargarProyectos(index);
    cargarRoles(index);
    cargarAreas(index);
}

function eliminarProyecto(index) {
    const item = document.querySelector(`.proyecto-item[data-index="${index}"]`);
    if (item) {
        item.remove();
    }
    proyectosAgregados.splice(index, 1);
    
    // Reindexar
    document.querySelectorAll('.proyecto-item').forEach((item, newIndex) => {
        item.dataset.index = newIndex;
        const headerStrong = item.querySelector('.proyecto-item-header strong');
        if (headerStrong) {
            headerStrong.innerHTML = `<i data-feather="folder" style="width: 16px; height: 16px; vertical-align: middle; margin-right: .35rem;"></i>Proyecto ${newIndex + 1}`;
        }
        const btnEliminar = item.querySelector('.btn');
        if (btnEliminar) {
            btnEliminar.setAttribute('onclick', `eliminarProyecto(${newIndex})`);
        }
    });
    
    // Reemplazar iconos de feather
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

function cargarProyectos(index) {
    fetch('/admin/roles/proyectos')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById(`proyecto_${index}`);
            if (!select) return;
            
            select.innerHTML = '<option value="">Seleccionar...</option>';
            data.proyectos.forEach(p => {
                select.innerHTML += `<option value="${p.idproyecto}">${p.nombre}</option>`;
            });
        })
        .catch(err => console.error('Error:', err));
}

function cargarRoles(index) {
    fetch('/admin/usuarios/roles')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById(`rol_${index}`);
            if (!select) return;
            
            select.innerHTML = '<option value="">Seleccionar...</option>';
            data.forEach(r => {
                select.innerHTML += `<option value="${r.idroles}">${r.nombrerol}</option>`;
            });
        })
        .catch(err => console.error('Error:', err));
}

function cargarAreas(index) {
    fetch('/admin/usuarios/areas')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById(`area_${index}`);
            if (!select) return;
            
            select.innerHTML = '<option value="">Seleccionar...</option>';
            data.forEach(a => {
                select.innerHTML += `<option value="${a.idarea}">${a.nombrearea}</option>`;
            });
        })
        .catch(err => console.error('Error:', err));
}

function guardarUsuario() {
    const dni = document.getElementById('dni').value.trim();
    const nombre = document.getElementById('nombre').value.trim();
    const correo = document.getElementById('correo').value.trim();
    const password = document.getElementById('password').value;
    
    if (!dni || !nombre || !password) {
        alert('DNI, nombre y contraseña son obligatorios');
        return;
    }
    
    if (proyectosAgregados.length === 0) {
        alert('Debes agregar al menos un proyecto');
        return;
    }
    
    // Recopilar asignaciones
    const asignaciones = [];
    for (let i = 0; i < proyectosAgregados.length; i++) {
        const proyecto = document.getElementById(`proyecto_${i}`)?.value;
        const rol = document.getElementById(`rol_${i}`)?.value;
        const area = document.getElementById(`area_${i}`)?.value;
        const cargo = document.getElementById(`cargo_${i}`)?.value;
        
        if (!proyecto || !rol || !area || !cargo) {
            alert('Completa todos los campos de los proyectos');
            return;
        }
        
        asignaciones.push({
            proyecto_id: proyecto,
            rol_id: rol,
            area_id: area,
            cargo: cargo,
            modulos: [] // Por ahora sin módulos
        });
    }
    
    const payload = {
        dni,
        nombre,
        correo: correo || null,
        password,
        asignaciones
    };
    
    console.log('Guardando:', payload);
    
    fetch('/admin/usuarios/crear-nuevo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            alert('Usuario creado exitosamente');
            cerrarModal();
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'No se pudo crear el usuario'));
        }
    })
    .catch(err => {
        console.error('Error:', err);
        alert('Error de conexión');
    });
}

function verDetalles(dni) {
    alert('Ver detalles de: ' + dni);
}
