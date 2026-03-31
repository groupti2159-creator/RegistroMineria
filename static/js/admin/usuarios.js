// Formulario simple de creación y edición de usuarios
// mostrarNotificacion: en otras pantallas viene de desvíos/ajax_handler.js; aquí no se carga ese script.

if (typeof window.mostrarNotificacion !== 'function') {
    window.mostrarNotificacion = function (mensaje, tipo = 'success') {
        const notif = document.createElement('div');
        notif.className = 'ajax-notificacion notif-' + tipo;
        const icon = tipo === 'success' ? 'check-circle' : tipo === 'error' ? 'x-circle' : 'info';
        notif.innerHTML = '<i data-feather="' + icon + '"></i><span>' + String(mensaje) + '</span>';
        document.body.appendChild(notif);
        if (typeof feather !== 'undefined') feather.replace();
        setTimeout(function () {
            notif.classList.add('fade-out');
            setTimeout(function () { notif.remove(); }, 300);
        }, 4000);
    };
}

let proyectosAgregados = [];
let usuarioEditando = null;

function setGuardarUsuarioLoading(loading) {
    const btn = document.getElementById('guardarUsuarioBtn');
    if (!btn) return;
    btn.disabled = !!loading;
    btn.setAttribute('aria-busy', loading ? 'true' : 'false');
}

function abrirModalCrear() {
    usuarioEditando = null;
    const modal = document.getElementById('modalCrearUsuario');
    modal.classList.add('open');
    proyectosAgregados = [];
    document.getElementById('formCrearUsuario').reset();
    document.getElementById('proyectos-container').innerHTML = '';
    document.getElementById('modalTitle').innerHTML = '<i data-feather="user-plus"></i> Crear Nuevo Usuario';
    document.getElementById('guardarUsuarioBtn').textContent = 'Guardar Usuario';
    document.getElementById('dni').disabled = false;
    document.getElementById('activo').value = '1';
    setGuardarUsuarioLoading(false);
    if (typeof feather !== 'undefined') feather.replace();
}

async function abrirModalEditar(dni) {
    setGuardarUsuarioLoading(true);
    try {
        const response = await fetch(`/admin/usuarios/detalle/${encodeURIComponent(dni)}`);
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'No se pudo cargar el usuario');
        }

        const u = data.usuario;
        usuarioEditando = dni;

        const modal = document.getElementById('modalCrearUsuario');
        modal.classList.add('open');
        proyectosAgregados = [];
        document.getElementById('formCrearUsuario').reset();
        document.getElementById('proyectos-container').innerHTML = '';
        document.getElementById('modalTitle').innerHTML = '<i data-feather="user-plus"></i> Editar Usuario';
        document.getElementById('guardarUsuarioBtn').textContent = 'Guardar Cambios';
        document.getElementById('dni').value = u.idusuario || '';
        document.getElementById('dni').disabled = true;
        document.getElementById('nombre').value = u.nombrecompleto || '';
        document.getElementById('correo').value = u.correo || '';
        document.getElementById('password').value = '';
        document.getElementById('activo').value = u.activo ? '1' : '0';

        const bloques = [];
        if (Array.isArray(data.asignaciones) && data.asignaciones.length) {
            for (const asig of data.asignaciones) {
                bloques.push(
                    agregarProyecto({
                        proyecto_id: asig.idproyecto,
                        rol_id: asig.idroles,
                        area_id: asig.idarea,
                        cargo: asig.cargo || '',
                        idusuariorol: asig.idusuariorol
                    })
                );
            }
        } else {
            bloques.push(agregarProyecto());
        }

        await Promise.all(bloques);

        if (typeof feather !== 'undefined') feather.replace();
    } catch (err) {
        console.error('Error al cargar usuario:', err);
        mostrarNotificacion(err.message || 'Error al cargar datos del usuario', 'error');
        const modal = document.getElementById('modalCrearUsuario');
        if (modal) modal.classList.remove('open');
    } finally {
        setGuardarUsuarioLoading(false);
    }
}

function cerrarModal() {
    const modal = document.getElementById('modalCrearUsuario');
    modal.classList.remove('open');
}

function agregarProyecto(asignacion) {
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
            <input type="hidden" id="idusuariorol_${index}" value="${asignacion?.idusuariorol || ''}">
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
    
    if (typeof feather !== 'undefined') feather.replace();
    
    // Listener para evitar proyectos duplicados
    const selectProy = document.getElementById(`proyecto_${index}`);
    selectProy.addEventListener('change', function() {
        validarProyectosDuplicados();
    });

    const hid = asignacion?.idusuariorol;
    if (hid != null && hid !== '') {
        const h = document.getElementById(`idusuariorol_${index}`);
        if (h) h.value = String(hid);
    }

    const p = cargarProyectos(index, asignacion?.proyecto_id);
    const r = cargarRoles(index, asignacion?.rol_id);
    const a = cargarAreas(index, asignacion?.area_id);
    if (asignacion?.cargo) {
        const c = document.getElementById(`cargo_${index}`);
        if (c) c.value = asignacion.cargo;
    }
    return Promise.all([p, r, a]);
}

function validarProyectosDuplicados() {
    const selects = document.querySelectorAll('#proyectos-container select[id^="proyecto_"]');
    const seleccionados = [];
    let hayDuplicados = false;

    selects.forEach(s => {
        s.style.borderColor = ''; // Limpiar errores previos
        if (s.value) {
            if (seleccionados.includes(s.value)) {
                s.style.borderColor = '#ef4444';
                hayDuplicados = true;
            }
            seleccionados.push(s.value);
        }
    });

    if (hayDuplicados) {
        mostrarNotificacion('No puedes asignar el mismo proyecto más de una vez', 'error');
    }
    return hayDuplicados;
}

function eliminarProyecto(index) {
    const item = document.querySelector(`.proyecto-item[data-index="${index}"]`);
    if (item) item.remove();
    proyectosAgregados.splice(index, 1);
    
    document.querySelectorAll('.proyecto-item').forEach((row, newIndex) => {
        row.dataset.index = newIndex;
        const headerStrong = row.querySelector('.proyecto-item-header strong');
        if (headerStrong) {
            headerStrong.innerHTML = `<i data-feather="folder" style="width: 16px; height: 16px; vertical-align: middle; margin-right: .35rem;"></i>Proyecto ${newIndex + 1}`;
        }
        const btnEliminar = row.querySelector('.proyecto-item-header .btn');
        if (btnEliminar) {
            btnEliminar.setAttribute('onclick', `eliminarProyecto(${newIndex})`);
        }
        const proyecto = row.querySelector('[id^="proyecto_"]');
        const rol = row.querySelector('[id^="rol_"]');
        const area = row.querySelector('[id^="area_"]');
        const cargo = row.querySelector('[id^="cargo_"]');
        const hid = row.querySelector('[id^="idusuariorol_"]');
        if (proyecto) proyecto.id = `proyecto_${newIndex}`;
        if (rol) rol.id = `rol_${newIndex}`;
        if (area) area.id = `area_${newIndex}`;
        if (cargo) cargo.id = `cargo_${newIndex}`;
        if (hid) hid.id = `idusuariorol_${newIndex}`;
    });
    
    if (typeof feather !== 'undefined') feather.replace();
}

function cargarProyectos(index, selectedId) {
    return fetch('/admin/roles/proyectos')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById(`proyecto_${index}`);
            if (!select) return;
            select.innerHTML = '<option value="">Seleccionar...</option>';
            data.proyectos.forEach(p => {
                select.innerHTML += `<option value="${p.idproyecto}">${p.nombre}</option>`;
            });
            if (selectedId != null && selectedId !== '') {
                select.value = String(selectedId);
            }
        });
}

function cargarRoles(index, selectedId) {
    return fetch('/admin/usuarios/roles')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById(`rol_${index}`);
            if (!select) return;
            select.innerHTML = '<option value="">Seleccionar...</option>';
            data.forEach(r => {
                select.innerHTML += `<option value="${r.idroles}">${r.nombrerol}</option>`;
            });
            if (selectedId != null && selectedId !== '') {
                select.value = String(selectedId);
            }
        });
}

function cargarAreas(index, selectedId) {
    return fetch('/admin/usuarios/areas')
        .then(r => r.json())
        .then(data => {
            const select = document.getElementById(`area_${index}`);
            if (!select) return;
            select.innerHTML = '<option value="">Seleccionar...</option>';
            data.forEach(a => {
                select.innerHTML += `<option value="${a.idarea}">${a.nombrearea}</option>`;
            });
            if (selectedId != null && selectedId !== '') {
                select.value = String(selectedId);
            }
        });
}

function guardarUsuario() {
    const dni = document.getElementById('dni').value.trim();
    const nombre = document.getElementById('nombre').value.trim();
    const correo = document.getElementById('correo').value.trim();
    const password = document.getElementById('password').value;
    const activo = document.getElementById('activo').value;
    const isEdit = usuarioEditando !== null;

    if (!nombre) {
        mostrarNotificacion('El nombre completo es obligatorio', 'error');
        document.getElementById('nombre').focus();
        return;
    }
    if (!isEdit && !dni) {
        mostrarNotificacion('El DNI es obligatorio', 'error');
        document.getElementById('dni').focus();
        return;
    }
    if (dni && !/^\d{8}$/.test(dni)) {
        mostrarNotificacion('El DNI debe tener 8 dígitos numéricos', 'error');
        document.getElementById('dni').focus();
        return;
    }
    if (correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
        mostrarNotificacion('El formato del correo electrónico no es válido', 'error');
        document.getElementById('correo').focus();
        return;
    }
    if (!isEdit && password.length < 6) {
        mostrarNotificacion('La contraseña debe tener al menos 6 caracteres', 'error');
        document.getElementById('password').focus();
        return;
    }
    if (isEdit && password.length > 0 && password.length < 6) {
        mostrarNotificacion('La nueva contraseña debe tener al menos 6 caracteres', 'error');
        document.getElementById('password').focus();
        return;
    }

    if (validarProyectosDuplicados()) return;

    const asignaciones = [];
    const items = document.querySelectorAll('#proyectos-container .proyecto-item');
    
    if (items.length === 0) {
        mostrarNotificacion('Debes agregar al menos un proyecto al usuario', 'error');
        return;
    }

    for (const item of items) {
        const selects = item.querySelectorAll('.form-select');
        const proyecto = selects[0]?.value ?? '';
        const rol = selects[1]?.value ?? '';
        const area = selects[2]?.value ?? '';
        const cargoEl = item.querySelector('input[id^="cargo_"]');
        const cargo = (cargoEl?.value ?? '').trim();
        const hid = item.querySelector('input[type="hidden"]');
        let idusuariorol = (hid?.value ?? '').trim() || null;

        if (!proyecto || !rol || !area || !cargo) {
            item.style.border = '2px solid #ef4444';
            mostrarNotificacion('Completa todos los campos obligatorios en cada proyecto (*) ', 'error');
            return;
        } else {
            item.style.border = '';
        }

        asignaciones.push({ idusuariorol, proyecto_id: proyecto, rol_id: rol, area_id: area, cargo });
    }

    const payload = {
        nombre,
        correo: correo || null,
        activo: Number(activo),
        password: password || '',
        asignaciones
    };

    let url = '/admin/usuarios/crear-nuevo';
    if (isEdit) {
        url = `/admin/usuarios/editar/${encodeURIComponent(usuarioEditando)}`;
    } else {
        payload.dni = dni;
    }

    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(async (r) => {
        let data;
        try {
            data = await r.json();
        } catch (e) {
            throw new Error(r.status ? `Respuesta no válida (${r.status})` : 'Respuesta no válida');
        }
        if (!r.ok || !data.success) {
            throw new Error(data.error || data.message || `Error ${r.status}`);
        }
        return data;
    })
    .then(() => {
        mostrarNotificacion(isEdit ? 'Usuario actualizado correctamente' : 'Usuario creado exitosamente', 'success');
        cerrarModal();
        location.reload();
    })
    .catch(err => {
        console.error('Error:', err);
        mostrarNotificacion(err.message || 'Error de conexión', 'error');
    });
}

function editarUsuario(dni) {
    abrirModalEditar(dni);
}