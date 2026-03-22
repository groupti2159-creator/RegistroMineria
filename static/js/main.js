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
  
  // Cerrar todos los otros submenus
  document.querySelectorAll('.nav-submenu.open').forEach(menu => {
    if (menu !== submenu) {
      menu.classList.remove('open');
      menu.previousElementSibling.classList.remove('open');
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

// ── INICIALIZAR ICONOS FEATHER ──
function initFeatherIcons() {
  if (typeof feather !== 'undefined') {
    feather.replace({ 'stroke-width': 1.2 });
  }
}

// Inicializar iconos cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initFeatherIcons);

// Reinicializar iconos cuando se abren modales
function observeModals() {
  const modals = document.querySelectorAll('.modal-overlay');
  modals.forEach(modal => {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.attributeName === 'style' && modal.style.display === 'flex') {
          setTimeout(initFeatherIcons, 50);
        }
      });
    });
    observer.observe(modal, { attributes: true });
  });
}

document.addEventListener('DOMContentLoaded', observeModals);

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

// Close modals on overlay click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.style.display = 'none';
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


// ── PREVIEW DE IMÁGENES ──
const _previewInstances = {};

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
function toggleProyectos() {
  const dropdown = document.getElementById('proyectoDropdown');
  const btn = document.getElementById('proyectoBtn');
  if (!dropdown || !btn) return;
  
  const isOpen = dropdown.classList.contains('open');
  
  if (isOpen) {
    dropdown.classList.remove('open');
    btn.classList.remove('open');
  } else {
    dropdown.classList.add('open');
    btn.classList.add('open');
    cargarProyectosDisponibles();
  }
}

function cargarProyectosDisponibles() {
  console.log('Iniciando carga de proyectos...');
  fetch('/proyectos/api/proyectos-disponibles')
    .then(r => {
      console.log('Respuesta recibida, status:', r.status);
      return r.json();
    })
    .then(data => {
      console.log('Proyectos recibidos:', data);
      const list = document.getElementById('proyectoList');
      console.log('Elemento proyectoList:', list);
      
      if (!list) {
        console.error('No se encontró el elemento proyectoList');
        return;
      }
      
      if (!data.success) {
        console.error('API retornó success=false:', data);
        list.innerHTML = '<div class="proyecto-loading">Error: ' + (data.error || 'Error desconocido') + '</div>';
        return;
      }
      
      if (!data.proyectos || data.proyectos.length === 0) {
        console.warn('No hay proyectos disponibles');
        list.innerHTML = '<div class="proyecto-loading">No hay proyectos disponibles</div>';
        return;
      }
      
      console.log('Generando HTML para', data.proyectos.length, 'proyectos');
      list.innerHTML = data.proyectos.map(p => `
        <div class="proyecto-item ${p.activo ? 'active' : ''}" 
             onclick="cambiarProyecto('${p.codigo}', '${p.nombre}')">
          <div class="proyecto-item-icon" style="background: #22c55e20; color: #22c55e">
            <i data-feather="folder"></i>
          </div>
          <div class="proyecto-item-info">
            <span class="proyecto-item-nombre">${p.nombre}</span>
            <span class="proyecto-item-desc">${p.descripcion || 'Sin descripción'}</span>
          </div>
          <span class="proyecto-item-check">✓</span>
        </div>
      `).join('');
      
      console.log('HTML generado, inicializando iconos Feather');
      // Inicializar iconos Feather
      if (typeof feather !== 'undefined') {
        feather.replace();
      }
    })
    .catch(err => {
      console.error('Error cargando proyectos:', err);
      const list = document.getElementById('proyectoList');
      if (list) list.innerHTML = '<div class="proyecto-loading">Error al cargar proyectos</div>';
    });
}

function cambiarProyecto(codigo, nombre) {
  // Cerrar dropdown
  const dropdown = document.getElementById('proyectoDropdown');
  const btn = document.getElementById('proyectoBtn');
  if (dropdown) dropdown.classList.remove('open');
  if (btn) btn.classList.remove('open');
  
  // Mostrar loading en el botón
  const nombreEl = document.getElementById('proyectoNombre');
  if (nombreEl) nombreEl.textContent = 'Cambiando...';
  
  // Hacer petición para cambiar proyecto
  fetch('/proyectos/api/cambiar-proyecto', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ codigo_proyecto: codigo })
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      // Actualizar nombre del proyecto en el botón
      if (nombreEl) nombreEl.textContent = nombre;
      
      // Redirigir al dashboard correspondiente según el proyecto
      if (codigo === 'DESVIOS_AMB') {
        // Ir al dashboard de desvíos ambientales
        window.location.href = '/admin/dashboard';
      } else {
        // Ir al dashboard genérico del proyecto
        window.location.href = '/proyectos/dashboard/' + codigo;
      }
    } else {
      alert('Error al cambiar proyecto: ' + (data.error || 'Error desconocido'));
      if (nombreEl) nombreEl.textContent = nombre;
    }
  })
  .catch(err => {
    console.error('Error:', err);
    alert('Error al cambiar proyecto');
    if (nombreEl) nombreEl.textContent = nombre;
  });
}

function cargarSidebarProyecto(codigo) {
  const sidebarNav = document.querySelector('.sidebar-nav');
  if (!sidebarNav) return;
  
  // Añadir clase de transición
  sidebarNav.classList.add('transitioning');
  
  // Cargar nuevo contenido del sidebar
  fetch('/proyectos/api/sidebar-proyecto')
    .then(r => r.text())
    .then(html => {
      setTimeout(() => {
        sidebarNav.innerHTML = html;
        sidebarNav.classList.remove('transitioning');
        sidebarNav.classList.add('loaded');
        
        setTimeout(() => {
          sidebarNav.classList.remove('loaded');
        }, 300);
      }, 150);
    })
    .catch(err => {
      console.error('Error cargando sidebar:', err);
      sidebarNav.classList.remove('transitioning');
    });
}

// Cargar nombre del proyecto al cargar la página
document.addEventListener('DOMContentLoaded', function() {
  // Cargar nombre del proyecto (solo si existe el selector)
  const nombreEl = document.getElementById('proyectoNombre');
  if (nombreEl) {
    fetch('/proyectos/api/proyectos-disponibles')
      .then(r => r.json())
      .then(data => {
        if (data.success && data.proyectos && data.proyectos.length > 0) {
          const proyectoActual = data.proyectos.find(p => p.activo) || data.proyectos[0];
          nombreEl.textContent = proyectoActual.nombre;
        } else {
          nombreEl.textContent = 'Sin proyecto';
        }
      })
      .catch(() => { nombreEl.textContent = 'Error'; });
  }
});



// ── NAVEGACIÓN SPA (carga de módulos sin recargar página) ──
(function initSpaNav() {
  // URLs que se manejan con navegación SPA (no recargan la página)
  const SPA_PATHS = [
    '/admin/compromisos',
    '/admin/meteorologia',
    '/admin/residuos/generacion',
    '/admin/residuos/comercializable',
    '/admin/residuos/matpel',
    '/admin/residuos/compostaje',
  ];

  // Títulos para el top-bar según la URL
  const PAGE_TITLES = {
    '/admin/compromisos': 'Compromisos',
    '/admin/meteorologia': 'Data Meteorológica',
    '/admin/residuos/generacion': 'Generación Diaria',
    '/admin/residuos/comercializable': 'Comercializable',
    '/admin/residuos/matpel': 'Disposición Matpel',
    '/admin/residuos/compostaje': 'Compostaje',
  };

  function loadModule(url) {
    const pageBody = document.querySelector('.page-body');
    if (!pageBody) return;

    // Mostrar loading
    pageBody.innerHTML = '<div class="loading-state" style="padding:4rem;text-align:center"><i data-feather="loader" style="width:32px;height:32px;color:var(--text-muted)"></i><p style="margin-top:1rem;color:var(--text-muted)">Cargando...</p></div>';
    if (typeof feather !== 'undefined') feather.replace({ 'stroke-width': 1.2 });

    fetch(url, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(r => {
        if (!r.ok) throw new Error('Error ' + r.status);
        return r.text();
      })
      .then(html => {
        pageBody.innerHTML = html;
        // Actualizar título del top-bar
        const titleEl = document.querySelector('.top-bar-title h1');
        if (titleEl && PAGE_TITLES[url]) titleEl.textContent = PAGE_TITLES[url];
        // Actualizar URL sin recargar
        history.pushState({ spaUrl: url }, '', url);
        // Reinicializar iconos feather
        if (typeof feather !== 'undefined') feather.replace({ 'stroke-width': 1.2 });
        // Marcar item activo en sidebar
        updateSidebarActive(url);
      })
      .catch(() => {
        pageBody.innerHTML = '<div class="empty-state" style="padding:4rem"><p style="color:var(--text-muted)">Error al cargar el módulo.</p></div>';
      });
  }

  function updateSidebarActive(url) {
    document.querySelectorAll('.nav-item, .nav-subitem').forEach(el => {
      el.classList.remove('active');
    });
    const match = document.querySelector(`.nav-item[href="${url}"], .nav-subitem[href="${url}"]`);
    if (match) {
      match.classList.add('active');
      // Abrir submenu padre si existe
      const submenu = match.closest('.nav-submenu');
      if (submenu) {
        submenu.classList.add('open');
        const toggle = submenu.previousElementSibling;
        if (toggle) toggle.classList.add('active');
      }
    }
  }

  // Interceptar clics en links del sidebar que sean rutas SPA
  document.addEventListener('click', function(e) {
    const link = e.target.closest('a.nav-item, a.nav-subitem');
    if (!link) return;
    const href = link.getAttribute('href');
    if (!href || !SPA_PATHS.includes(href)) return;
    e.preventDefault();
    loadModule(href);
    if (window.innerWidth <= 768) closeMobileMenu();
  });

  // Manejar botón atrás/adelante del navegador
  window.addEventListener('popstate', function(e) {
    if (e.state && e.state.spaUrl) {
      loadModule(e.state.spaUrl);
    }
  });
})();
