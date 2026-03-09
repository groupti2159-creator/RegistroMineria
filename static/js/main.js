// ── DARK MODE ──
function toggleDark() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', isDark ? 'light' : 'dark');
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
  const btn = document.getElementById('darkToggle');
  if (btn) btn.querySelector('.nav-icon').textContent = isDark ? '🌙' : '☀️';
}

(function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  const btn = document.getElementById('darkToggle');
  if (btn && saved === 'dark') btn.querySelector('.nav-icon').textContent = '☀️';
})();

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
          <div class="notif-item ${n.Leida ? '' : 'unread'}" onclick="marcarNotif('${n.IdNotificacion}', this)">
            <p>${n.Mensaje}</p>
            <small>${n.FechaCreacion}</small>
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
function setupImagePreview(inputId, previewContainerId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  
  let selectedFiles = [];
  
  input.addEventListener('change', function(e) {
    const files = Array.from(e.target.files);
    selectedFiles = files.slice(0, 5); // Máximo 5 imágenes
    
    renderPreview();
    updateFileLabel(inputId);
  });
  
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
  
  window.removePreviewImage = function(inputId, previewContainerId, index) {
    const input = document.getElementById(inputId);
    selectedFiles.splice(index, 1);
    
    // Actualizar el input con los archivos restantes
    const dt = new DataTransfer();
    selectedFiles.forEach(file => dt.items.add(file));
    input.files = dt.files;
    
    renderPreview();
    updateFileLabel(inputId);
  };
  
  function updateFileLabel(inputId) {
    const nameEl = document.querySelector(`label[for="${inputId}"] .file-name`);
    if (!nameEl) return;
    
    if (selectedFiles.length === 0) {
      nameEl.textContent = 'Sin archivos seleccionados';
    } else if (selectedFiles.length === 1) {
      nameEl.textContent = selectedFiles[0].name;
    } else {
      nameEl.textContent = `${selectedFiles.length} archivos seleccionados`;
    }
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
  
  // Establecer en el campo de fecha de ejecución
  const fechaEjecInput = document.querySelector('input[name="fecha_ejecucion"]');
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
