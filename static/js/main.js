// ── CONSTANTES GLOBALES ──────────────────────────────────────────────────────────
const _previewInstances = {};



// ── DARK MODE ──
function toggleDark() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  const newTheme = isDark ? 'light' : 'dark';
  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  
  // Update toggle button text and icon
  const toggleBtn = document.getElementById('darkToggle');
  if (toggleBtn) {
    const textSpan = toggleBtn.querySelector('span:not(.nav-icon)');
    const iconSpan = toggleBtn.querySelector('.nav-icon');
    if (newTheme === 'dark') {
      if (textSpan) textSpan.textContent = 'Modo Claro';
      if (iconSpan) iconSpan.innerHTML = '<i data-feather="sun"></i>';
    } else {
      if (textSpan) textSpan.textContent = 'Modo Oscuro';
      if (iconSpan) iconSpan.innerHTML = '<i data-feather="moon"></i>';
    }
    // Reinitialize feather icons
    if (typeof feather !== 'undefined') {
      feather.replace({ 'stroke-width': 1.2 });
    }
  }
}

(function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  
  // Update toggle button on page load
  const toggleBtn = document.getElementById('darkToggle');
  if (toggleBtn && saved === 'dark') {
    const textSpan = toggleBtn.querySelector('span:not(.nav-icon)');
    const iconSpan = toggleBtn.querySelector('.nav-icon');
    if (textSpan) textSpan.textContent = 'Modo Claro';
    if (iconSpan) iconSpan.innerHTML = '<i data-feather="sun"></i>';
  }
})();

// ── MOBILE MENU ──
function toggleMobileMenu() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  
  if (sidebar && overlay) {
    sidebar.classList.toggle('open');
    overlay.classList.toggle('open');
  }
}

function closeMobileMenu() {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  
  if (sidebar && overlay) {
    sidebar.classList.remove('open');
    overlay.classList.remove('open');
  }
}

// ── SIDEBAR SUBMENU ──
function toggleSubmenu(button) {
  const submenu = button.nextElementSibling;
  const isOpen = submenu.classList.contains('open');

  // Cerrar otros submenus del mismo nivel (no los padres)
  const parentSubmenu = button.closest('.nav-submenu');
  const selector = parentSubmenu ? '.nav-submenu.open' : '.nav-group > .nav-submenu.open';
  document.querySelectorAll(selector).forEach(menu => {
    if (menu !== submenu && !menu.contains(button)) {
      menu.classList.remove('open');
      const btn = menu.previousElementSibling;
      if (btn) btn.classList.remove('active');
    }
  });

  // Toggle el submenu actual
  if (isOpen) {
    submenu.classList.remove('open');
    button.classList.remove('open');
  } else {
    submenu.classList.add('open');
    button.classList.add('open');
  }

  // Reinicializar iconos
  if (typeof feather !== 'undefined') {
    feather.replace({ 'stroke-width': 1.2 });
  }
}

// ── RIPPLE EFFECT ──
function createRipple(event) {
  const button = event.currentTarget;
  
  // Remover ripples anteriores
  const existingRipple = button.querySelector('.ripple');
  if (existingRipple) {
    existingRipple.remove();
  }
  
  const circle = document.createElement('span');
  const diameter = Math.max(button.clientWidth, button.clientHeight);
  const radius = diameter / 2;
  
  const rect = button.getBoundingClientRect();
  circle.style.width = circle.style.height = `${diameter}px`;
  circle.style.left = `${event.clientX - rect.left - radius}px`;
  circle.style.top = `${event.clientY - rect.top - radius}px`;
  circle.classList.add('ripple');
  
  button.appendChild(circle);
  
  setTimeout(() => {
    circle.remove();
  }, 600);
}

// Cerrar menú al hacer clic en un enlace (móvil)
document.addEventListener('DOMContentLoaded', function() {
  const navItems = document.querySelectorAll('.nav-item, .nav-subitem');
  navItems.forEach(item => {
    // Agregar efecto ripple
    item.addEventListener('click', createRipple);
    
    // Cerrar menú móvil
    item.addEventListener('click', function() {
      if (window.innerWidth <= 768 && !item.classList.contains('nav-toggle')) {
        closeMobileMenu();
      }
    });
  });
  
  // Cerrar menú al cambiar tamaño de ventana
  window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
      closeMobileMenu();
    }
  });
});

// ── MODALES GLOBALES ─────────────────────────────────────────────────────────────
function abrirModal(id) {
  const modal = typeof id === 'string' ? document.getElementById(id) : id;
  if (!modal) return;
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
  // Reinicializar iconos dentro del modal
  if (typeof feather !== 'undefined') {
    setTimeout(() => feather.replace({ 'stroke-width': 1.2 }), 10);
  }
}

function cerrarModal(id) {
  const modal = typeof id === 'string' ? document.getElementById(id) : id;
  if (!modal) return;
  modal.classList.remove('open');
  
  // Verificar si quedan otros modales abiertos antes de restaurar el scroll
  const openModals = document.querySelectorAll('.modal-overlay.open');
  if (openModals.length === 0) {
    document.body.style.overflow = '';
  }
}

// ── TOAST / NOTIFICACIONES ──
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) {
    const newContainer = document.createElement('div');
    newContainer.id = 'toast-container';
    newContainer.style.cssText = 'position:fixed;top:1.5rem;right:1.5rem;z-index:10000;display:flex;flex-direction:column;gap:0.75rem;pointer-events:none;';
    document.body.appendChild(newContainer);
  }
  
  const toast = document.createElement('div');
  toast.className = `alert alert-${type} toast-animate-in`;
  toast.style.cssText = 'pointer-events:auto;min-width:300px;box-shadow:var(--shadow-lg);margin:0;';
  
  let icon = 'info';
  if (type === 'success') icon = 'check-circle';
  if (type === 'error' || type === 'danger') icon = 'x-circle';
  if (type === 'warning') icon = 'alert-triangle';

  toast.innerHTML = `
    <div style="display:flex;align-items:center;gap:0.75rem;width:100%;">
      <i data-feather="${icon}" style="width:18px;height:18px;flex-shrink:0;"></i>
      <span style="flex:1;font-weight:500;">${message}</span>
      <button onclick="this.parentElement.parentElement.remove()" style="background:none;border:none;cursor:pointer;padding:4px;color:currentColor;opacity:0.7;display:flex;">
        <i data-feather="x" style="width:16px;height:16px;"></i>
      </button>
    </div>
  `;
  
  document.getElementById('toast-container').appendChild(toast);
  if (typeof feather !== 'undefined') feather.replace();
  
  // Auto-remove
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }, 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    // Cerrar modales al hacer clic en el overlay (fondo)
    document.addEventListener('click', e => {
      if (e.target.classList.contains('modal-overlay')) {
        cerrarModal(e.target);
      }
    });

    // Cerrar modales con la tecla Escape
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal-overlay.open');
        if (openModal) cerrarModal(openModal);
      }
    });
});




// ── NOTIFICATIONS ──
function toggleNotifPanel() {
  const panel = document.getElementById('notifPanel');
  if (!panel) return;
  panel.classList.toggle('open');
  if (panel.classList.contains('open')) loadNotifs();
}

function loadNotifs() {
  fetch('/api/notificaciones')
    .then(r => r.json())
    .then(data => {
      const list  = document.getElementById('notifList');
      const badge = document.getElementById('notifCount');
      if (!list) return;
      if (!data.notifs || data.notifs.length === 0) {
        list.innerHTML = '<div class="notif-empty">Sin notificaciones nuevas</div>';
      } else {
        list.innerHTML = data.notifs.map(n => `
          <div class="notif-item ${n.leida ? '' : 'unread'}" onclick="marcarNotif('${n.idnotificacion}', this)">
            <p>${n.mensaje}</p>
            <small>${n.fechacreacion}</small>
          </div>`).join('');
      }
      if (badge) {
        badge.textContent = data.count;
        badge.style.display = data.count > 0 ? 'block' : 'none';
      }
    }).catch(() => {});
}

function marcarNotif(id, el) {
  const base = window.location.pathname.startsWith('/admin') ? '/admin' : '/supervisor';
  fetch(`${base}/notificaciones/leer/${id}`, {method:'POST'})
    .then(() => { if (el) el.classList.remove('unread'); loadNotifs(); });
}

function marcarTodas() {
  const base = window.location.pathname.startsWith('/admin') ? '/admin' : '/supervisor';
  fetch(`${base}/notificaciones/todas`, {method:'POST'})
    .then(() => { loadNotifs(); });
}

// Close notif panel on outside click
document.addEventListener('click', e => {
  const panel = document.getElementById('notifPanel');
  const btn   = document.getElementById('notifBtn');
  if (panel && btn && !btn.contains(e.target) && !panel.contains(e.target)) {
    panel.classList.remove('open');
  }
});



// File input labels
document.addEventListener('change', e => {
  if (e.target.classList.contains('file-input') || e.target.type === 'file') {
    const nameEl = e.target.nextElementSibling?.querySelector('.file-name');
    if (!nameEl) return;
    const files = e.target.files;
    if (files.length === 0) nameEl.textContent = 'Sin archivos seleccionados';
    else if (files.length === 1) nameEl.textContent = files[0].name;
    else nameEl.textContent = `${files.length} archivos seleccionados`;
  }
});

// Lightbox
document.addEventListener('click', e => {
  if (e.target.classList.contains('img-thumb')) {
    openLightbox(e.target.src);
  }
});

function openLightbox(src) {
  let lb = document.getElementById('lightbox');
  if (!lb) {
    lb = document.createElement('div');
    lb.id = 'lightbox';
    lb.innerHTML = `<button id="lightbox-close" onclick="document.getElementById('lightbox').classList.remove('open')">✕</button><img id="lightbox-img" src="">`;
    document.body.appendChild(lb);
  }
  document.getElementById('lightbox-img').src = src;
  lb.classList.add('open');
}

// Auto-hide alerts
setTimeout(() => {
  document.querySelectorAll('.alert').forEach(a => {
    a.style.transition = 'opacity .5s';
    a.style.opacity = '0';
    setTimeout(() => a.remove(), 500);
  });
}, 4000);




function removePreviewImage(inputId, previewContainerId, index) {
  const instance = _previewInstances[inputId];
  if (!instance) return;
  instance.removeFile(index);
}

function setupImagePreview(inputId, previewContainerId) {
  const input = document.getElementById(inputId);
  if (!input) return;

  // Remover listener anterior para evitar acumulación
  if (input._previewHandler) {
    input.removeEventListener('change', input._previewHandler);
  }

  let selectedFiles = [];

  const instance = {
    removeFile(index) {
      selectedFiles.splice(index, 1);
      const dt = new DataTransfer();
      selectedFiles.forEach(file => dt.items.add(file));
      input.files = dt.files;
      renderPreview();
      updateFileLabel();
    },
    reset() {
      selectedFiles = [];
    }
  };
  _previewInstances[inputId] = instance;

  input._previewHandler = function(e) {
    selectedFiles = Array.from(e.target.files).slice(0, 5);
    renderPreview();
    updateFileLabel();
  };
  input.addEventListener('change', input._previewHandler);

  function renderPreview() {
    const container = document.getElementById(previewContainerId);
    if (!container) return;
    if (selectedFiles.length === 0) {
      container.innerHTML = '';
      container.style.display = 'none';
      return;
    }
    container.style.display = 'grid';
    container.innerHTML = '';
    selectedFiles.forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = function(e) {
        const div = document.createElement('div');
        div.className = 'image-preview-item';
        div.innerHTML = `
          <img src="${e.target.result}" alt="${file.name}">
          <button type="button" class="image-preview-remove" onclick="removePreviewImage('${inputId}', '${previewContainerId}', ${index})">✕</button>
          <div class="image-preview-name">${file.name}</div>
        `;
        container.appendChild(div);
      };
      reader.readAsDataURL(file);
    });
  }

  function updateFileLabel() {
    const nameEl = document.querySelector(`label[for="${inputId}"] .file-name`);
    if (!nameEl) return;
    if (selectedFiles.length === 0) nameEl.textContent = 'Sin archivos seleccionados';
    else if (selectedFiles.length === 1) nameEl.textContent = selectedFiles[0].name;
    else nameEl.textContent = `${selectedFiles.length} archivos seleccionados`;
  }
}

// Inicializar previews cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  // Para el modal de crear
  setupImagePreview('fileEvidencias', 'previewEvidencias');
  setupImagePreview('fileLevantamientos', 'previewLevantamientos');
  
  // Para el modal de subir (supervisor)
  setupImagePreview('fileSubirImagenes', 'previewSubirImagenes');
});

// Limpia el formulario de crear y todos sus previews
function resetFormCrear() {
  var modalCrear = document.getElementById('modalCrear');
  if (!modalCrear) return;
  var form = modalCrear.querySelector('form');
  if (form) form.reset();
  ['fileEvidencias', 'fileLevantamientos'].forEach(function(inputId) {
    var previewId = inputId === 'fileEvidencias' ? 'previewEvidencias' : 'previewLevantamientos';
    var instance = _previewInstances[inputId];
    if (instance) instance.reset();
    var container = document.getElementById(previewId);
    if (container) { container.innerHTML = ''; container.style.display = 'none'; }
    var nameEl = document.querySelector('label[for="' + inputId + '"] .file-name');
    if (nameEl) nameEl.textContent = 'Sin archivos seleccionados';
  });
  // Re-setear fechas después del reset
  setDefaultDate();
}


// ── FECHA AUTOMÁTICA (Zona horaria Perú) ──
function setDefaultDate() {
  // Obtener fecha actual en zona horaria de Perú (UTC-5)
  const now = new Date();
  const peruOffset = -5 * 60; // Perú está en UTC-5
  const localOffset = now.getTimezoneOffset();
  const peruTime = new Date(now.getTime() + (localOffset + peruOffset) * 60000);
  
  // Formatear como YYYY-MM-DD para input type="date"
  const year = peruTime.getFullYear();
  const month = String(peruTime.getMonth() + 1).padStart(2, '0');
  const day = String(peruTime.getDate()).padStart(2, '0');
  const dateString = `${year}-${month}-${day}`;
  
  // Establecer en el campo de fecha de inicio
  const fechaInput = document.getElementById('fecha_inicio');
  if (fechaInput && !fechaInput.value) {
    fechaInput.value = dateString;
  }
  
  // Establecer en el campo de fecha de ejecución (solo del modal crear, no del editar)
  const fechaEjecInput = document.querySelector('#modalCrear input[name="fecha_ejecucion"]');
  if (fechaEjecInput && !fechaEjecInput.value) {
    fechaEjecInput.value = dateString;
  }
}

// Ejecutar cuando se abre el modal de crear
document.addEventListener('DOMContentLoaded', function() {
  const modalCrear = document.getElementById('modalCrear');
  if (modalCrear) {
    // Observar cuando se abre el modal
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (modalCrear.style.display === 'flex') {
          setDefaultDate();
        }
      });
    });
    
    observer.observe(modalCrear, { attributes: true, attributeFilter: ['style'] });
  }
});


// ── PROYECTO SELECTOR ──
// ELIMINADO: El selector de proyectos solo debe estar en el login
// Las funciones toggleProyectos, cargarProyectosDisponibles y cambiarProyecto han sido removidas



// ── NAVEGACIÓN SPA (carga de módulos sin recargar página) ──
(function initSpaNav() {
  // SPA deshabilitado — navegación normal para todos los módulos
  // Cada clic recarga la página completa con el layout base
})();
