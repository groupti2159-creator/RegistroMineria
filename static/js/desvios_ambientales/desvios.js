// ── ELIMINAR REGISTRO ──
async function eliminarRegistro(rid, codigo) {
  if (!confirm(`¿Eliminar el registro "${codigo}"?\nEsta acción no se puede deshacer.`)) return;
  try {
    const res = await fetch(ELIMINAR_URL_BASE + rid, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });
    const json = await res.json();
    if (json.success) {
      // Quitar la fila de la tabla sin recargar
      const fila = document.querySelector(`button[onclick*="${rid}"]`)?.closest('tr');
      if (fila) {
        fila.style.transition = 'opacity .3s';
        fila.style.opacity = '0';
        setTimeout(() => { fila.remove(); }, 300);
      } else {
        location.reload();
      }
    } else {
      alert('Error al eliminar: ' + (json.error || 'Error desconocido'));
    }
  } catch(e) {
    alert('Error de conexión');
  }
}

// ── DETALLE MODAL ──
function buildDetalleHTML(data) {
  const raw  = data.registro || {};
  // normalizar claves a minúsculas por si el servidor envía mixed-case
  const r = {};
  for (const k in raw) r[k.toLowerCase()] = raw[k];

  const normalize = arr => (arr||[]).map(obj => { const n={}; for(const k in obj) n[k.toLowerCase()]=obj[k]; return n; });
  const ev = normalize(data.evidencias);
  const lv = normalize(data.levantamientos);

  const estadoColor = {
    'Pendiente':'#92400e','En Proceso':'#1e40af','Enviado':'#6b21a8',
    'En Revisión':'#4c1d95','Culminado':'#166534','Rechazado':'#991b1b','Cerrado':'#475569'
  };
  const color = estadoColor[r.estado] || '#475569';

  const renderImgs = (imgs) => {
    if (!imgs.length) return '<p style="color:#94a3b8;font-size:.78rem">Sin imágenes</p>';
    return `<div class="img-gallery">${imgs.map(i => {
      const statusClass = i.estadoimagen === 'Aprobada' ? 'aprobada' : i.estadoimagen === 'Rechazada' ? 'rechazada' : 'pendiente';
      const src = '/static/' + i.rutaimagen;
      return `<div class="img-thumb-wrapper">
        <img class="img-thumb" src="${src}" title="${i.nombrearchivo||''}">
        <span class="img-status-dot ${statusClass}" title="${i.estadoimagen}"></span>
        ${i.motivorechazo ? `<small style="display:block;color:#ef4444;font-size:.65rem;max-width:80px">${i.motivorechazo}</small>` : ''}
      </div>`;
    }).join('')}</div>`;
  };

  const canValidate = typeof IS_ADMIN !== 'undefined' && IS_ADMIN;

  return `
  <div class="detalle-grid">
    <div>
      <div class="detalle-section">
        <div class="detalle-section-title"><i data-feather="info"></i> Información General</div>
        <div class="detalle-body">
          <div class="detalle-row">
            <div class="detalle-field"><label>Fecha</label><p>${r.fechainicio||'—'}</p></div>
            <div class="detalle-field"><label>Correlativo</label><p><code>${r.codigo||'—'}</code></p></div>
          </div>
          <div class="detalle-row">
            <div class="detalle-field"><label>Fecha Ejecución</label><p>${r.fechaejecucion||'—'}</p></div>
            <div class="detalle-field"><label>Riesgo</label><p style="color:#dc2626;font-weight:700">${r.riesgo||'—'}</p></div>
          </div>
        </div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title"><i data-feather="map-pin"></i> Ubicación</div>
        <div class="detalle-body"><p>${r.ubicacion||'—'}</p></div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title"><i data-feather="alert-triangle"></i> Detalle del Incidente</div>
        <div class="detalle-body">
          <div class="detalle-field" style="margin-bottom:.6rem">
            <label>Problema Detectado</label>
            <p>${r.descripcion||'—'}</p>
          </div>
          <div class="detalle-field">
            <label>Peligro Identificado</label>
            <p>${r.descripciontipo||'—'}</p>
          </div>
        </div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title"><i data-feather="check-square"></i> Acción Realizada</div>
        <div class="detalle-body"><p>${r.accion||'—'}</p></div>
      </div>
    </div>

    <div>
      <div class="detalle-section">
        <div class="detalle-section-title"><i data-feather="activity"></i> Estado del Reporte</div>
        <div class="detalle-body">
          <div class="estado-display" style="color:${color}">${r.estado||'—'}</div>
          <p style="font-size:.7rem;text-align:center;color:#94a3b8">Estado actual</p>
        </div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title"><i data-feather="briefcase"></i> Área Reportante</div>
        <div class="detalle-body"><p style="font-weight:600">${r.areareportante||'—'}</p></div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title"><i data-feather="users"></i> Responsables</div>
        <div class="detalle-body">
          <div class="detalle-field" style="margin-bottom:.4rem">
            <label>Área Responsable</label>
            <p style="font-weight:600">${r.arearesponsable||'—'}</p>
          </div>
          <div class="detalle-field" style="margin-bottom:.4rem">
            <label>CCTA Responsable</label>
            <p style="font-weight:600">${r.nombrecctaresponsable||'—'}</p>
          </div>
          <div class="detalle-field">
            <label>Personal Responsable</label>
            <p>${r.personalresponsable||'—'}</p>
          </div>
          <div class="detalle-field">
            <label>DNI Responsable</label>
            <p>${r.dniresponsable||'—'}</p>
          </div>
        </div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title"><i data-feather="image"></i> Evidencias</div>
        <div class="detalle-body">
          <p style="font-size:.72rem;font-weight:600;color:#94a3b8;margin-bottom:.4rem;display:flex;align-items:center;gap:.3rem"><i data-feather="image" style="width:14px;height:14px"></i> Evidencias (${ev.length})</p>
          ${renderImgs(ev)}
          <p style="font-size:.72rem;font-weight:600;color:#94a3b8;margin:.6rem 0 .4rem;display:flex;align-items:center;gap:.3rem"><i data-feather="file" style="width:14px;height:14px"></i> Levantamientos (${lv.length})</p>
          ${renderImgs(lv)}
          ${canValidate && lv.filter(i => i.estadoimagen === 'Pendiente').length > 0 ? 
            `<button onclick="abrirValidarConjunto('${r.idregistro}', ${JSON.stringify(lv).replace(/"/g, '&quot;')})" 
                     style="width:100%;margin-top:.8rem;padding:.6rem;background:#059669;color:white;border:none;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem;display:flex;align-items:center;justify-content:center;gap:.4rem">
              <i data-feather="check-circle" style="width:16px;height:16px"></i> Validar Conjunto de Imágenes
            </button>` : ''}
        </div>
      </div>

      <p style="font-size:.7rem;color:#94a3b8;text-align:center;margin-top:.5rem">
        Reporte generado el ${r.fechacreacion||'—'}
      </p>
    </div>
  </div>`;
}

function verDetalle(rid) {
  const url = DETALLE_URL_BASE + rid;
  document.getElementById('detalleContent').innerHTML = '<div class="loading-state">Cargando...</div>';
  document.getElementById('modalDetalle').classList.add('open');
  fetch(url).then(r => r.json()).then(data => {
    document.getElementById('detalleContent').innerHTML = buildDetalleHTML(data);
    // Inicializar iconos Feather después de cargar el contenido
    setTimeout(() => {
      if (typeof feather !== 'undefined') {
        feather.replace({ 'stroke-width': 1.2 });
      }
    }, 50);
  });
}

// ── EDITAR MODAL ──
let imagenesEditarEliminar = [];

function editarRegistro(rid) {
  const url = DETALLE_URL_BASE + rid;
  imagenesEditarEliminar = [];
  
  fetch(url).then(r => r.json()).then(data => {
    const raw = data.registro || {};
    // normalizar claves a minúsculas
    const r = {};
    for (const k in raw) r[k.toLowerCase()] = raw[k];
    const form = document.getElementById('formEditar');
    form.action = EDITAR_URL_BASE + rid;

    const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
    setVal('edit_fecha',       r.fechainicio ? r.fechainicio.substring(0,10) : '');
    setVal('edit_fecha_ejec',  r.fechaejecucion ? r.fechaejecucion.substring(0,10) : '');
    setVal('edit_descripcion', r.descripcion);
    setVal('edit_accion',      r.accion);
    setVal('edit_personal',    r.personalresponsable);
    setVal('edit_dni',         r.dniresponsable);
    setVal('edit_ccta',        r.cctaresponsable);
    setVal('edit_area_rep',    r.idareareportante);
    setVal('edit_area_res',    r.idarearesponsable);
    setVal('edit_ubicacion',   r.ubicacion);
    setVal('edit_riesgo',      r.idriesgo);
    setVal('edit_tipo',        r.iddescripciontipo);
    setVal('edit_estado',      r.idestado);
    setVal('edit_origen',      r.idorigen);

    // Cargar imágenes existentes
    renderEditImagenes(data.evidencias || [], data.levantamientos || []);

    document.getElementById('modalEditar').classList.add('open');
  });
}

// Interceptar el submit del formulario de edición para agregar las imágenes a eliminar
// (manejado por ajax_handler.js que lee imagenesEditarEliminar directamente)

function renderEditImagenes(evidencias, levantamientos) {
  const section = document.getElementById('edit_imagenes_section');
  if (!section) return;
  
  const totalImagenes = evidencias.length + levantamientos.length;
  
  let html = '';
  
  if (totalImagenes === 0) {
    html += '<p style="color:#94a3b8;font-size:.85rem;margin-bottom:1rem">No hay imágenes cargadas</p>';
  } else {
    html += '<div style="margin-bottom:1rem">';
    
    if (evidencias.length > 0) {
      html += '<p style="font-size:.85rem;font-weight:600;color:#64748b;margin-bottom:.5rem">🖼️ Evidencias (' + evidencias.length + ')</p>';
      html += '<div class="edit-images-grid">';
      evidencias.forEach(img => {
        const id = img.idimagen || img.IdImagen || '';
        const ruta = img.rutaimagen || img.RutaImagen || '';
        const nombre = img.nombrearchivo || img.NombreArchivo || 'Imagen';
        html += `
          <div class="edit-image-item" data-img-id="${id}">
            <img src="/static/${ruta}" alt="${nombre}">
            <button type="button" class="edit-image-delete" onclick="eliminarImagenEditar('${id}')" title="Eliminar imagen">✕</button>
            <div class="edit-image-name">${nombre}</div>
          </div>`;
      });
      html += '</div>';
    }
    
    if (levantamientos.length > 0) {
      html += '<p style="font-size:.85rem;font-weight:600;color:#64748b;margin:.8rem 0 .5rem">✏️ Levantamientos (' + levantamientos.length + ')</p>';
      html += '<div class="edit-images-grid">';
      levantamientos.forEach(img => {
        const id = img.idimagen || img.IdImagen || '';
        const ruta = img.rutaimagen || img.RutaImagen || '';
        const nombre = img.nombrearchivo || img.NombreArchivo || 'Imagen';
        html += `
          <div class="edit-image-item" data-img-id="${id}">
            <img src="/static/${ruta}" alt="${nombre}">
            <button type="button" class="edit-image-delete" onclick="eliminarImagenEditar('${id}')" title="Eliminar imagen">✕</button>
            <div class="edit-image-name">${nombre}</div>
          </div>`;
      });
      html += '</div>';
    }
    html += '</div>';
  }
  
  html += `
    <div style="margin-top:1rem;padding-top:1rem;border-top:1px solid #e2e8f0">
      <p style="font-size:.85rem;font-weight:600;color:#64748b;margin-bottom:.8rem">➕ Agregar Nuevas Imágenes</p>
      <div class="form-group" style="margin-bottom:1rem">
        <label class="form-label">🖼️ NUEVAS EVIDENCIAS</label>
        <div class="file-upload-area">
          <input type="file" name="nuevas_evidencias" multiple accept="image/*" class="file-input" id="editFileEvidencias">
          <label for="editFileEvidencias" class="file-label">
            <span class="btn btn-outline-green">Elegir archivos</span>
            <span class="file-name" id="editNameEvidencias">Sin archivos seleccionados</span>
          </label>
          <small class="form-hint">ℹ Máx 5 imágenes, 16MB cada una</small>
        </div>
        <div id="editPreviewEvidencias" class="image-preview-container" style="display:none"></div>
      </div>
      <div class="form-group">
        <label class="form-label">✏️ NUEVOS LEVANTAMIENTOS</label>
        <div class="file-upload-area">
          <input type="file" name="nuevos_levantamientos" multiple accept="image/*" class="file-input" id="editFileLevantamientos">
          <label for="editFileLevantamientos" class="file-label">
            <span class="btn btn-outline-green">Elegir archivos</span>
            <span class="file-name" id="editNameLevantamientos">Sin archivos seleccionados</span>
          </label>
          <small class="form-hint">ℹ Máx 5 imágenes, 16MB cada una</small>
        </div>
        <div id="editPreviewLevantamientos" class="image-preview-container" style="display:none"></div>
      </div>
    </div>`;
  
  section.innerHTML = html;
  
  // Configurar previews — llamar directamente, los elementos ya están en el DOM
  setupImagePreviewEdit('editFileEvidencias', 'editPreviewEvidencias', 'editNameEvidencias');
  setupImagePreviewEdit('editFileLevantamientos', 'editPreviewLevantamientos', 'editNameLevantamientos');
}

function eliminarImagenEditar(imagenId) {
  if (!confirm('¿Eliminar esta imagen permanentemente?')) return;
  
  imagenesEditarEliminar.push(imagenId);
  
  // Ocultar visualmente la imagen
  const item = document.querySelector(`.edit-image-item[data-img-id="${imagenId}"]`);
  if (item) {
    item.style.opacity = '0.3';
    item.style.pointerEvents = 'none';
    const deleteBtn = item.querySelector('.edit-image-delete');
    if (deleteBtn) deleteBtn.style.display = 'none';
  }
}

function setupImagePreviewEdit(inputId, previewContainerId, nameId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  
  let selectedFiles = [];
  
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
        div.dataset.index = index;
        div.innerHTML = `
          <img src="${e.target.result}" alt="${file.name}">
          <button type="button" class="image-preview-remove" title="Quitar">✕</button>
          <div class="image-preview-name">${file.name}</div>`;
        div.querySelector('.image-preview-remove').addEventListener('click', () => {
          selectedFiles.splice(index, 1);
          const dt = new DataTransfer();
          selectedFiles.forEach(f => dt.items.add(f));
          input.files = dt.files;
          renderPreview();
          updateLabel();
        });
        container.appendChild(div);
      };
      reader.readAsDataURL(file);
    });
  }
  
  function updateLabel() {
    const nameEl = document.getElementById(nameId);
    if (!nameEl) return;
    if (selectedFiles.length === 0) nameEl.textContent = 'Sin archivos seleccionados';
    else if (selectedFiles.length === 1) nameEl.textContent = selectedFiles[0].name;
    else nameEl.textContent = `${selectedFiles.length} archivos seleccionados`;
  }
  
  input.addEventListener('change', function() {
    selectedFiles = Array.from(this.files).slice(0, 5);
    renderPreview();
    updateLabel();
  });
}

// ── SUBIR MODAL (supervisor) ──
function abrirSubirModal(rid) {
  const form = document.getElementById('formSubir');
  if (form) {
    // Limpiar formulario antes de abrir
    form.reset();
    
    // Usar la función global de limpieza si existe
    if (typeof window.limpiarPreviewSubir === 'function') {
      window.limpiarPreviewSubir();
    } else {
      // Fallback: limpiar manualmente
      const previewContainer = document.getElementById('previewSubirImagenes');
      if (previewContainer) {
        previewContainer.innerHTML = '';
        previewContainer.style.display = 'none';
      }
      
      const nameEl = document.getElementById('nameSubir');
      if (nameEl) {
        nameEl.textContent = 'Sin archivos seleccionados';
      }
      
      const fileInput = document.getElementById('fileSubirImagenes');
      if (fileInput) {
        fileInput.value = '';
      }
    }
    
    // Establecer action del formulario
    form.action = SUBIR_URL_BASE + rid;
    
    // Abrir modal
    document.getElementById('modalSubir').classList.add('open');
  }
}

// ── VALIDAR IMAGEN (admin) ──
let imagenesValidar = [];
let imagenesOriginales = [];

function abrirValidarConjunto(registroId, levantamientos) {
  // Filtrar solo imágenes pendientes
  imagenesOriginales = levantamientos.filter(img => img.estadoimagen === 'Pendiente');
  imagenesValidar = [...imagenesOriginales]; // Copia para manipular
  
  if (imagenesValidar.length === 0) {
    alert('No hay imágenes pendientes de validación');
    return;
  }
  
  document.getElementById('formValidar').action = VALIDAR_URL_BASE + registroId;
  renderValidarGallery();
  document.getElementById('modalDetalle').classList.remove('open');
  document.getElementById('modalValidar').classList.add('open');
}

function renderValidarGallery() {
  const gallery = document.getElementById('validarGallery');
  if (imagenesValidar.length === 0) {
    gallery.innerHTML = '<p style="color:#ef4444;text-align:center">Debes mantener al menos 1 imagen</p>';
    return;
  }
  
  gallery.innerHTML = imagenesValidar.map((img, index) => {
    const src = '/static/' + img.rutaimagen;
    return `
      <div class="validar-img-item" data-index="${index}">
        <img src="${src}" alt="${img.nombrearchivo || ''}">
        <button type="button" class="validar-img-delete" onclick="eliminarImagenValidar(${index})" title="Eliminar esta imagen">
          ✕
        </button>
        <div class="validar-img-info">
          ${img.nombrearchivo || 'Imagen ' + (index + 1)}
        </div>
      </div>
    `;
  }).join('');
  
  // Actualizar campos hidden
  const idsAprobar = imagenesValidar.map(img => img.idimagen).join(',');
  const idsRechazar = imagenesOriginales.map(img => img.idimagen).join(',');
  document.getElementById('validarImagenesIds').value = idsAprobar;
  document.getElementById('validarImagenesIdsRechazar').value = idsRechazar;
}

function eliminarImagenValidar(index) {
  if (imagenesValidar.length <= 1) {
    alert('Debe quedar al menos 1 imagen para validar');
    return;
  }
  
  if (confirm('¿Eliminar esta imagen del conjunto? (Se borrará permanentemente si apruebas)')) {
    imagenesValidar.splice(index, 1);
    renderValidarGallery();
  }
}

function validarFormulario() {
  if (imagenesValidar.length === 0) {
    alert('Debe quedar al menos 1 imagen para validar');
    return false;
  }
  return true;
}

function cerrarModalValidar() {
  document.getElementById('modalValidar').classList.remove('open');
  document.getElementById('validarComentario').value = '';
  imagenesValidar = [];
  imagenesOriginales = [];
}

// Función legacy para compatibilidad (ya no se usa)
function abrirValidar(imagenId, imgSrc, registroId) {
  // Esta función ya no se usa, pero la mantenemos por compatibilidad
  console.warn('abrirValidar is deprecated, use abrirValidarConjunto instead');
}


// ── VALIDACIÓN DE FORMULARIO DE CREAR ──
document.addEventListener('DOMContentLoaded', function() {
  const modalCrear = document.getElementById('modalCrear');
  if (!modalCrear) return;
  
  const formCrear = modalCrear.querySelector('form');
  if (!formCrear) return;
  
  const btnGuardar = document.getElementById('btnGuardarReporte');
  if (!btnGuardar) return;
  
  // Campos obligatorios
  const camposObligatorios = {
    fecha_inicio: formCrear.querySelector('[name="fecha_inicio"]'),
    area_reportante: formCrear.querySelector('[name="area_reportante"]'),
    fecha_ejecucion: formCrear.querySelector('[name="fecha_ejecucion"]'),
    ubicacion: formCrear.querySelector('[name="ubicacion"]'),
    descripcion: formCrear.querySelector('[name="descripcion"]'),
    riesgo: formCrear.querySelector('[name="riesgo"]'),
    tipo: formCrear.querySelector('[name="tipo"]'),
    area_responsable: formCrear.querySelector('[name="area_responsable"]'),
    evidencias: document.getElementById('fileEvidencias')
  };
  
  // Función para validar todos los campos
  function validarFormulario() {
    let todosCompletos = true;
    
    // Validar campos de texto y selects
    for (let key in camposObligatorios) {
      const campo = camposObligatorios[key];
      if (!campo) continue;
      
      if (key === 'evidencias') {
        // Validar que haya al menos 1 imagen
        if (!campo.files || campo.files.length === 0) {
          todosCompletos = false;
          break;
        }
      } else if (campo.tagName === 'SELECT') {
        // Validar selects
        if (!campo.value || campo.value === '') {
          todosCompletos = false;
          break;
        }
      } else if (campo.tagName === 'TEXTAREA' || campo.tagName === 'INPUT') {
        // Validar inputs y textareas
        if (!campo.value || campo.value.trim() === '') {
          todosCompletos = false;
          break;
        }
        // Validar longitud mínima para descripción
        if (key === 'descripcion' && campo.value.trim().length < 10) {
          todosCompletos = false;
          break;
        }
      }
    }
    
    // Habilitar o deshabilitar botón
    if (todosCompletos) {
      btnGuardar.disabled = false;
      btnGuardar.style.opacity = '1';
      btnGuardar.style.cursor = 'pointer';
    } else {
      btnGuardar.disabled = true;
      btnGuardar.style.opacity = '0.5';
      btnGuardar.style.cursor = 'not-allowed';
    }
  }
  
  // Agregar listeners a todos los campos
  for (let key in camposObligatorios) {
    const campo = camposObligatorios[key];
    if (!campo) continue;
    
    if (key === 'evidencias') {
      campo.addEventListener('change', validarFormulario);
    } else {
      campo.addEventListener('input', validarFormulario);
      campo.addEventListener('change', validarFormulario);
    }
  }
  
  // Validar al abrir el modal
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.target === modalCrear && modalCrear.classList.contains('open')) {
        // Poner fecha y hora actual si el campo está vacío
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm   = String(today.getMonth() + 1).padStart(2, '0');
        const dd   = String(today.getDate()).padStart(2, '0');
        const hh   = String(today.getHours()).padStart(2, '0');
        const min  = String(today.getMinutes()).padStart(2, '0');
        
        const fechaHoy = yyyy + '-' + mm + '-' + dd;
        const fechaHoraHoy = yyyy + '-' + mm + '-' + dd + 'T' + hh + ':' + min;
        
        const fInicio = formCrear.querySelector('[name="fecha_inicio"]');
        const fEjec   = formCrear.querySelector('[name="fecha_ejecucion"]');
        
        if (fInicio && !fInicio.value) fInicio.value = fechaHoraHoy;
        if (fEjec   && !fEjec.value)   fEjec.value   = fechaHoraHoy;
        
        validarFormulario();
      }
    });
  });
  
  observer.observe(modalCrear, { attributes: true, attributeFilter: ['class'] });
  
  // Agregar validación personalizada antes del submit
  formCrear.addEventListener('submit', function(e) {
    const fileEvidencias = document.getElementById('fileEvidencias');
    
    // Verificar si hay archivos seleccionados
    if (!fileEvidencias || !fileEvidencias.files || fileEvidencias.files.length === 0) {
      e.preventDefault();
      e.stopPropagation();
      
      // Mostrar mensaje de error
      alert('⚠️ Debes subir al menos 1 imagen de evidencia para crear el reporte.');
      
      // Hacer scroll al campo de evidencias
      fileEvidencias.scrollIntoView({ behavior: 'smooth', block: 'center' });
      
      // Resaltar el campo
      const fileLabel = fileEvidencias.closest('.file-upload-area');
      if (fileLabel) {
        fileLabel.style.border = '2px solid #ef4444';
        setTimeout(() => {
          fileLabel.style.border = '';
        }, 3000);
      }
      
      return false;
    }
    
    // Si hay archivos, permitir el envío
    return true;
  });
  
  // Validación inicial
  validarFormulario();
});


// ── AUTO-APERTURA DE MODAL DESDE URL ──
// Detectar si hay parámetro ver_detalle en la URL y abrir el modal automáticamente
document.addEventListener('DOMContentLoaded', function() {
  const urlParams = new URLSearchParams(window.location.search);
  const verDetalleId = urlParams.get('ver_detalle');
  
  if (verDetalleId) {
    // Esperar un momento para que la página cargue completamente
    setTimeout(function() {
      // Verificar si la función verDetalle existe
      if (typeof verDetalle === 'function') {
        verDetalle(verDetalleId);
      } else {
        // Fallback manual si la función no está disponible
        const url = DETALLE_URL_BASE + verDetalleId;
        document.getElementById('detalleContent').innerHTML = '<div class="loading-state">Cargando...</div>';
        document.getElementById('modalDetalle').classList.add('open');
        fetch(url).then(r => r.json()).then(data => {
          document.getElementById('detalleContent').innerHTML = buildDetalleHTML(data);
          setTimeout(() => {
            if (typeof feather !== 'undefined') {
              feather.replace({ 'stroke-width': 1.2 });
            }
          }, 50);
        });
      }
      
      // Limpiar el parámetro de la URL sin recargar la página
      const newUrl = window.location.pathname + (urlParams.toString().replace(/[?&]ver_detalle=[^&]*/g, '') ? '?' + urlParams.toString().replace(/[?&]ver_detalle=[^&]*/g, '').replace(/^&/, '') : '');
      window.history.replaceState({}, '', newUrl);
    }, 500);
  }
});

// ── VALIDACIÓN EN TIEMPO REAL ─────────────────────────────────────────────
function validarCampo(el) {
  const tag = el.tagName.toLowerCase();
  let lleno = false;

  if (tag === 'select') {
    lleno = el.value !== '' && el.value !== '0';
  } else if (tag === 'textarea') {
    lleno = el.value.trim().length >= (parseInt(el.getAttribute('minlength') || 1));
  } else {
    lleno = el.value.trim() !== '';
  }

  // Solo aplicar si el campo es requerido o ya fue tocado
  const requerido = el.hasAttribute('required');
  if (!requerido && el.value.trim() === '') {
    el.classList.remove('field-valid', 'field-invalid');
    return;
  }

  el.classList.toggle('field-valid',   lleno);
  el.classList.toggle('field-invalid', !lleno);
}

function activarValidacionTiempoReal(formId) {
  const form = document.getElementById(formId);
  if (!form) return;

  const campos = form.querySelectorAll(
    'input[type="text"], input[type="date"], input[type="email"], select, textarea'
  );

  campos.forEach(el => {
    // Al perder el foco: validar siempre
    el.addEventListener('blur', () => validarCampo(el));
    // Al escribir/cambiar: validar solo si ya tiene clase (fue tocado)
    el.addEventListener('input', () => {
      if (el.classList.contains('field-valid') || el.classList.contains('field-invalid')) {
        validarCampo(el);
      }
    });
    el.addEventListener('change', () => validarCampo(el));
  });
}

document.addEventListener('DOMContentLoaded', function () {
  // Activar en modal crear
  activarValidacionTiempoReal('modalCrear');

  // Activar en modal editar cuando se abre (los campos se llenan dinámicamente)
  const observer = new MutationObserver(() => {
    const form = document.getElementById('formEditar');
    if (form && !form.dataset.validacionActiva) {
      form.dataset.validacionActiva = '1';
      activarValidacionTiempoReal('formEditar');
    }
  });
  const modalEditar = document.getElementById('modalEditar');
  if (modalEditar) {
    observer.observe(modalEditar, { attributes: true, attributeFilter: ['class'] });
  }

  // Limpiar clases al resetear el modal crear
  const btnCancelar = document.querySelectorAll('[onclick*="modalCrear"]');
  btnCancelar.forEach(btn => {
    btn.addEventListener('click', () => {
      const form = document.querySelector('#modalCrear form');
      if (form) {
        form.querySelectorAll('.field-valid, .field-invalid').forEach(el => {
          el.classList.remove('field-valid', 'field-invalid');
        });
      }
    });
  });
});

// ── PREVIEW DE IMÁGENES PARA MODAL DE SUBIR ──
// Versión simplificada: solo mostrar contador, sin preview de imágenes
(function() {
  let previewInitialized = false;
  
  function initializePreview() {
    if (previewInitialized) return;
    
    const fileInput = document.getElementById('fileSubirImagenes');
    if (!fileInput) return;
    
    previewInitialized = true;
    
    // Solo actualizar el contador de archivos
    fileInput.addEventListener('change', function() {
      const nameEl = document.getElementById('nameSubir');
      if (!nameEl) return;
      
      const count = this.files.length;
      
      if (count === 0) {
        nameEl.textContent = 'Sin archivos seleccionados';
      } else if (count === 1) {
        nameEl.textContent = this.files[0].name;
      } else {
        nameEl.textContent = `${count} archivos seleccionados`;
      }
    });
    
    // Función global para limpiar
    window.limpiarPreviewSubir = function() {
      const nameEl = document.getElementById('nameSubir');
      if (nameEl) {
        nameEl.textContent = 'Sin archivos seleccionados';
      }
      
      if (fileInput) {
        fileInput.value = '';
      }
      
      // Ocultar contenedor de preview si existe
      const container = document.getElementById('previewSubirImagenes');
      if (container) {
        container.innerHTML = '';
        container.style.display = 'none';
      }
    };
  }
  
  // Inicializar cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePreview);
  } else {
    initializePreview();
  }
})();


// ── CARGAR PERSONAL POR ÁREA ──
async function cargarPersonalPorArea(idArea) {
  const selectPersonal = document.getElementById('personal_reportante');
  
  if (!idArea) {
    selectPersonal.innerHTML = '<option value="">Primero selecciona un área...</option>';
    selectPersonal.disabled = true;
    return;
  }
  
  try {
    selectPersonal.innerHTML = '<option value="">Cargando personal...</option>';
    selectPersonal.disabled = true;
    
    const res = await fetch(`/admin/api/personal-por-area/${idArea}`);
    const data = await res.json();
    
    if (data.success && data.personal && data.personal.length > 0) {
      selectPersonal.innerHTML = '<option value="">Seleccionar personal...</option>';
      data.personal.forEach(p => {
        const option = document.createElement('option');
        option.value = p.id;
        option.textContent = p.NombresCompletos;
        selectPersonal.appendChild(option);
      });
      selectPersonal.disabled = false;
    } else {
      selectPersonal.innerHTML = '<option value="">No hay personal disponible</option>';
      selectPersonal.disabled = true;
    }
  } catch (error) {
    console.error('Error cargando personal:', error);
    selectPersonal.innerHTML = '<option value="">Error al cargar personal</option>';
    selectPersonal.disabled = true;
  }
}


// ── CARGAR RIESGOS CRÍTICOS POR TIPO ──
async function cargarRiesgosCriticos(idTipo) {
  const selectRiesgo = document.getElementById('riesgo_critico');
  
  if (!idTipo) {
    selectRiesgo.innerHTML = '<option value="">Primero selecciona un tipo...</option>';
    selectRiesgo.disabled = true;
    return;
  }
  
  try {
    selectRiesgo.innerHTML = '<option value="">Cargando riesgos...</option>';
    selectRiesgo.disabled = true;
    
    const res = await fetch(`/admin/api/riesgos-criticos-por-tipo/${idTipo}`);
    const data = await res.json();
    
    if (data.success && data.riesgos && data.riesgos.length > 0) {
      selectRiesgo.innerHTML = '<option value="">Seleccionar riesgo crítico...</option>';
      data.riesgos.forEach(r => {
        const option = document.createElement('option');
        option.value = r.id;
        option.textContent = `${r.codigo}. ${r.descripcion}`;
        selectRiesgo.appendChild(option);
      });
      selectRiesgo.disabled = false;
    } else {
      selectRiesgo.innerHTML = '<option value="">No hay riesgos disponibles</option>';
      selectRiesgo.disabled = true;
    }
  } catch (error) {
    console.error('Error cargando riesgos críticos:', error);
    selectRiesgo.innerHTML = '<option value="">Error al cargar riesgos</option>';
    selectRiesgo.disabled = true;
  }
}


// ── CARGAR PERSONAL RESPONSABLE (todo el personal activo) ──
// Se usa /api/todo-personal porque tbl_persona solo tiene idareareportante
// pero el área responsable es una tabla distinta (tbl_arearesponsable)
async function cargarPersonalResponsable(idArea) {
  // idArea se ignora — cargamos todo el personal disponible
  const selectPersonal = document.getElementById('personal_responsable_id');
  if (!selectPersonal) return;
  
  try {
    selectPersonal.innerHTML = '<option value="">Cargando personal...</option>';
    selectPersonal.disabled = true;
    
    const res = await fetch('/admin/api/todo-personal');
    const data = await res.json();
    
    if (data.success && data.personal && data.personal.length > 0) {
      selectPersonal.innerHTML = '<option value="">Seleccionar personal...</option>';
      data.personal.forEach(p => {
        const option = document.createElement('option');
        option.value = p.id;
        option.textContent = p.NombresCompletos;
        selectPersonal.appendChild(option);
      });
      selectPersonal.disabled = false;
    } else {
      selectPersonal.innerHTML = '<option value="">No hay personal disponible</option>';
      selectPersonal.disabled = true;
    }
  } catch (error) {
    console.error('Error cargando personal responsable:', error);
    selectPersonal.innerHTML = '<option value="">Error al cargar personal</option>';
    selectPersonal.disabled = true;
  }
}

// Cargar personal responsable automáticamente al abrir el modal crear
document.addEventListener('DOMContentLoaded', function() {
  const modalCrear = document.getElementById('modalCrear');
  if (!modalCrear) return;
  const obs = new MutationObserver(function(mutations) {
    mutations.forEach(function(m) {
      if (modalCrear.classList.contains('open')) {
        cargarPersonalResponsable(null);
      }
    });
  });
  obs.observe(modalCrear, { attributes: true, attributeFilter: ['class'] });
});
