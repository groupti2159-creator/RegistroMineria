// ── DETALLE MODAL ──
function buildDetalleHTML(data) {
  const r  = data.registro || {};
  const ev = data.evidencias || [];
  const lv = data.levantamientos || [];

  const estadoColor = {
    'Pendiente':'#92400e','En Proceso':'#1e40af','Enviado':'#6b21a8',
    'En Revisión':'#4c1d95','Culminado':'#166534','Rechazado':'#991b1b','Cerrado':'#475569'
  };
  const color = estadoColor[r.Estado] || '#475569';

  const renderImgs = (imgs, showValidar, registroId) => {
    if (!imgs.length) return '<p style="color:#94a3b8;font-size:.78rem">Sin imágenes</p>';
    return `<div class="img-gallery">${imgs.map(i => {
      const statusClass = i.EstadoImagen === 'Aprobada' ? 'aprobada' : i.EstadoImagen === 'Rechazada' ? 'rechazada' : 'pendiente';
      const src = '/static/' + i.RutaImagen;
      return `<div class="img-thumb-wrapper">
        <img class="img-thumb" src="${src}" title="${i.NombreArchivo||''}">
        <span class="img-status-dot ${statusClass}" title="${i.EstadoImagen}"></span>
        ${i.MotivoRechazo ? `<small style="display:block;color:#ef4444;font-size:.65rem;max-width:80px">${i.MotivoRechazo}</small>` : ''}
      </div>`;
    }).join('')}</div>`;
  };

  const canValidate = typeof IS_ADMIN !== 'undefined' && IS_ADMIN;

  return `
  <div class="detalle-grid">
    <div>
      <div class="detalle-section">
        <div class="detalle-section-title">🔵 Información General</div>
        <div class="detalle-body">
          <div class="detalle-row">
            <div class="detalle-field"><label>Fecha</label><p>${r.FechaInicio||'—'}</p></div>
            <div class="detalle-field"><label>Correlativo</label><p><code>${r.Codigo||'—'}</code></p></div>
          </div>
          <div class="detalle-row">
            <div class="detalle-field"><label>Fecha Ejecución</label><p>${r.FechaEjecucion||'—'}</p></div>
            <div class="detalle-field"><label>Riesgo</label><p style="color:#dc2626;font-weight:700">${r.Riesgo||'—'}</p></div>
          </div>
        </div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title">📍 Ubicación</div>
        <div class="detalle-body"><p>${r.Ubicacion||'—'}</p></div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title">⚠️ Detalle del Incidente</div>
        <div class="detalle-body">
          <div class="detalle-field" style="margin-bottom:.6rem">
            <label>Problema Detectado</label>
            <p>${r.Descripcion||'—'}</p>
          </div>
          <div class="detalle-field">
            <label>Peligro Identificado</label>
            <p>${r.DescripcionTipo||'—'}</p>
          </div>
        </div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title">✅ Acción Realizada</div>
        <div class="detalle-body"><p>${r.Accion||'—'}</p></div>
      </div>
    </div>

    <div>
      <div class="detalle-section">
        <div class="detalle-section-title">📊 Estado del Reporte</div>
        <div class="detalle-body">
          <div class="estado-display" style="color:${color}">${r.Estado||'—'}</div>
          <p style="font-size:.7rem;text-align:center;color:#94a3b8">Estado actual</p>
        </div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title">🏢 Área Reportante</div>
        <div class="detalle-body"><p style="font-weight:600">${r.AreaReportante||'—'}</p></div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title">👥 Responsables</div>
        <div class="detalle-body">
          <div class="detalle-field" style="margin-bottom:.4rem">
            <label>Área Responsable</label>
            <p style="font-weight:600">${r.AreaResponsable||'—'}</p>
          </div>
          <div class="detalle-field">
            <label>Personal Responsable</label>
            <p>${r.PersonalResponsable||'—'}</p>
          </div>
        </div>
      </div>

      <div class="detalle-section">
        <div class="detalle-section-title">🖼️ Evidencias</div>
        <div class="detalle-body">
          <p style="font-size:.72rem;font-weight:600;color:#94a3b8;margin-bottom:.4rem">🖼 Evidencias (${ev.length})</p>
          ${renderImgs(ev, false, r.IdRegistro)}
          <p style="font-size:.72rem;font-weight:600;color:#94a3b8;margin:.6rem 0 .4rem">✏️ Levantamientos (${lv.length})</p>
          ${renderImgs(lv, false, r.IdRegistro)}
          ${canValidate && lv.filter(i => i.EstadoImagen === 'Pendiente').length > 0 ? 
            `<button onclick="abrirValidarConjunto('${r.IdRegistro}', ${JSON.stringify(lv).replace(/"/g, '&quot;')})" 
                     style="width:100%;margin-top:.8rem;padding:.6rem;background:#059669;color:white;border:none;border-radius:6px;font-weight:600;cursor:pointer;font-size:.85rem">
              ✅ Validar Conjunto de Imágenes
            </button>` : ''}
        </div>
      </div>

      <p style="font-size:.7rem;color:#94a3b8;text-align:center;margin-top:.5rem">
        Reporte generado el ${r.FechaCreacion||'—'}
      </p>
    </div>
  </div>`;
}

function verDetalle(rid) {
  const url = DETALLE_URL_BASE + rid;
  document.getElementById('detalleContent').innerHTML = '<div class="loading-state">Cargando...</div>';
  document.getElementById('modalDetalle').style.display = 'flex';
  fetch(url).then(r => r.json()).then(data => {
    document.getElementById('detalleContent').innerHTML = buildDetalleHTML(data);
  });
}

// ── EDITAR MODAL ──
let imagenesEditarEliminar = [];

function editarRegistro(rid) {
  const url = DETALLE_URL_BASE + rid;
  imagenesEditarEliminar = [];
  
  fetch(url).then(r => r.json()).then(data => {
    const r = data.registro || {};
    const form = document.getElementById('formEditar');
    form.action = EDITAR_URL_BASE + rid;

    const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
    setVal('edit_fecha',       r.FechaInicio ? r.FechaInicio.substring(0,10) : '');
    setVal('edit_fecha_ejec',  r.FechaEjecucion ? r.FechaEjecucion.substring(0,10) : '');
    setVal('edit_descripcion', r.Descripcion);
    setVal('edit_accion',      r.Accion);
    setVal('edit_personal',    r.PersonalResponsable);
    setVal('edit_area_rep',    r.idAreaReportante);
    setVal('edit_area_res',    r.idAreaResponsable);
    setVal('edit_ubicacion',   r.idUbicacion);
    setVal('edit_riesgo',      r.IdRiesgo);
    setVal('edit_tipo',        r.IdDescripcionTipo);
    setVal('edit_estado',      r.idEstado);

    // Cargar imágenes existentes
    renderEditImagenes(data.evidencias || [], data.levantamientos || []);

    document.getElementById('modalEditar').style.display = 'flex';
  });
}

// Interceptar el submit del formulario de edición para agregar las imágenes a eliminar
document.addEventListener('DOMContentLoaded', function() {
  const formEditar = document.getElementById('formEditar');
  if (formEditar) {
    formEditar.addEventListener('submit', function(e) {
      // Agregar campo hidden con las imágenes a eliminar
      let inputEliminar = document.querySelector('input[name="imagenes_eliminar"]');
      if (!inputEliminar) {
        inputEliminar = document.createElement('input');
        inputEliminar.type = 'hidden';
        inputEliminar.name = 'imagenes_eliminar';
        formEditar.appendChild(inputEliminar);
      }
      inputEliminar.value = imagenesEditarEliminar.join(',');
    });
  }
});

function renderEditImagenes(evidencias, levantamientos) {
  const section = document.getElementById('edit_imagenes_section');
  if (!section) return;
  
  const totalImagenes = evidencias.length + levantamientos.length;
  
  if (totalImagenes === 0) {
    section.innerHTML = '<p style="color:#94a3b8;font-size:.85rem">No hay imágenes cargadas por el administrador</p>';
    return;
  }
  
  let html = '<div style="margin-bottom:1rem">';
  
  // Evidencias
  if (evidencias.length > 0) {
    html += '<p style="font-size:.85rem;font-weight:600;color:#64748b;margin-bottom:.5rem">🖼️ Evidencias (' + evidencias.length + ')</p>';
    html += '<div class="edit-images-grid">';
    evidencias.forEach(img => {
      html += `
        <div class="edit-image-item" data-img-id="${img.IdImagen}">
          <img src="/static/${img.RutaImagen}" alt="${img.NombreArchivo || ''}">
          <button type="button" class="edit-image-delete" onclick="eliminarImagenEditar('${img.IdImagen}')" title="Eliminar imagen">✕</button>
          <div class="edit-image-name">${img.NombreArchivo || 'Imagen'}</div>
        </div>
      `;
    });
    html += '</div>';
  }
  
  // Levantamientos
  if (levantamientos.length > 0) {
    html += '<p style="font-size:.85rem;font-weight:600;color:#64748b;margin:.8rem 0 .5rem">✏️ Levantamientos (' + levantamientos.length + ')</p>';
    html += '<div class="edit-images-grid">';
    levantamientos.forEach(img => {
      html += `
        <div class="edit-image-item" data-img-id="${img.IdImagen}">
          <img src="/static/${img.RutaImagen}" alt="${img.NombreArchivo || ''}">
          <button type="button" class="edit-image-delete" onclick="eliminarImagenEditar('${img.IdImagen}')" title="Eliminar imagen">✕</button>
          <div class="edit-image-name">${img.NombreArchivo || 'Imagen'}</div>
        </div>
      `;
    });
    html += '</div>';
  }
  
  html += '</div>';
  
  // Agregar inputs para nuevas imágenes
  html += `
    <div style="margin-top:1.5rem;padding-top:1rem;border-top:1px solid #e2e8f0">
      <p style="font-size:.85rem;font-weight:600;color:#64748b;margin-bottom:.8rem">➕ Agregar Nuevas Imágenes</p>
      
      <div class="form-group" style="margin-bottom:1rem">
        <label class="form-label">🖼️ NUEVAS EVIDENCIAS</label>
        <div class="file-upload-area">
          <input type="file" name="nuevas_evidencias" multiple accept="image/*" class="file-input" id="editFileEvidencias">
          <label for="editFileEvidencias" class="file-label">
            <span class="btn btn-outline-green">Elegir archivos</span>
            <span class="file-name" id="editNameEvidencias">Sin archivos seleccionados</span>
          </label>
          <small class="form-hint">ℹ Puedes seleccionar múltiples imágenes (Max 5, 16MB cada una)</small>
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
          <small class="form-hint">ℹ Puedes seleccionar múltiples imágenes (Max 5, 16MB cada una)</small>
        </div>
        <div id="editPreviewLevantamientos" class="image-preview-container" style="display:none"></div>
      </div>
    </div>
  `;
  
  section.innerHTML = html;
  
  // Configurar previews para nuevas imágenes
  setTimeout(() => {
    setupImagePreviewEdit('editFileEvidencias', 'editPreviewEvidencias');
    setupImagePreviewEdit('editFileLevantamientos', 'editPreviewLevantamientos');
  }, 100);
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

function setupImagePreviewEdit(inputId, previewContainerId) {
  const input = document.getElementById(inputId);
  if (!input) return;
  
  let selectedFiles = [];
  
  input.addEventListener('change', function(e) {
    const files = Array.from(e.target.files);
    selectedFiles = files.slice(0, 5);
    
    renderPreviewEdit();
    updateFileLabelEdit(inputId);
  });
  
  function renderPreviewEdit() {
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
          <button type="button" class="image-preview-remove" onclick="removePreviewImageEdit('${inputId}', '${previewContainerId}', ${index})">✕</button>
          <div class="image-preview-name">${file.name}</div>
        `;
        container.appendChild(div);
      };
      reader.readAsDataURL(file);
    });
  }
  
  window.removePreviewImageEdit = function(inputId, previewContainerId, index) {
    const input = document.getElementById(inputId);
    selectedFiles.splice(index, 1);
    
    const dt = new DataTransfer();
    selectedFiles.forEach(file => dt.items.add(file));
    input.files = dt.files;
    
    renderPreviewEdit();
    updateFileLabelEdit(inputId);
  };
  
  function updateFileLabelEdit(inputId) {
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

// ── SUBIR MODAL (supervisor) ──
function abrirSubirModal(rid) {
  const form = document.getElementById('formSubir');
  if (form) {
    form.action = SUBIR_URL_BASE + rid;
    document.getElementById('modalSubir').style.display = 'flex';
  }
}

// ── VALIDAR IMAGEN (admin) ──
let imagenesValidar = [];
let imagenesOriginales = [];

function abrirValidarConjunto(registroId, levantamientos) {
  // Filtrar solo imágenes pendientes
  imagenesOriginales = levantamientos.filter(img => img.EstadoImagen === 'Pendiente');
  imagenesValidar = [...imagenesOriginales]; // Copia para manipular
  
  if (imagenesValidar.length === 0) {
    alert('No hay imágenes pendientes de validación');
    return;
  }
  
  document.getElementById('formValidar').action = VALIDAR_URL_BASE + registroId;
  renderValidarGallery();
  document.getElementById('modalDetalle').style.display = 'none';
  document.getElementById('modalValidar').style.display = 'flex';
}

function renderValidarGallery() {
  const gallery = document.getElementById('validarGallery');
  if (imagenesValidar.length === 0) {
    gallery.innerHTML = '<p style="color:#ef4444;text-align:center">Debes mantener al menos 1 imagen</p>';
    return;
  }
  
  gallery.innerHTML = imagenesValidar.map((img, index) => {
    const src = '/static/' + img.RutaImagen;
    return `
      <div class="validar-img-item" data-index="${index}">
        <img src="${src}" alt="${img.NombreArchivo || ''}">
        <button type="button" class="validar-img-delete" onclick="eliminarImagenValidar(${index})" title="Eliminar esta imagen">
          ✕
        </button>
        <div class="validar-img-info">
          ${img.NombreArchivo || 'Imagen ' + (index + 1)}
        </div>
      </div>
    `;
  }).join('');
  
  // Actualizar campos hidden
  const idsAprobar = imagenesValidar.map(img => img.IdImagen).join(',');
  const idsRechazar = imagenesOriginales.map(img => img.IdImagen).join(',');
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
  document.getElementById('modalValidar').style.display = 'none';
  document.getElementById('validarComentario').value = '';
  imagenesValidar = [];
  imagenesOriginales = [];
}

// Función legacy para compatibilidad (ya no se usa)
function abrirValidar(imagenId, imgSrc, registroId) {
  // Esta función ya no se usa, pero la mantenemos por compatibilidad
  console.warn('abrirValidar is deprecated, use abrirValidarConjunto instead');
}

// ── ARCHIVAR confirm ──
function confirmarEliminar(rid) {
  if (confirm('Este reporte no está culminado. Solo se pueden archivar reportes CULMINADOS.')) {
    alert('El reporte debe estar en estado CULMINADO para ser archivado.');
  }
}
