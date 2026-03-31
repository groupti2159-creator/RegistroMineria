// ════════════════════════════════════════════════════════
//  ecoSupervisor — Compromisos / registro.js
// ════════════════════════════════════════════════════════


// ── CAMBIO DE PERÍODO ────────────────────────────────────
function cambiarPeriodo() {
  const mes  = document.getElementById('selMes').value;
  const anio = document.getElementById('selAnio').value;
  window.location.href = `/admin/compromisos?mes=${mes}&anio=${anio}`;
}


// ── TOAST ────────────────────────────────────────────────
// Usando showToast global de main.js


// ── POPOVER DE VERSIONES ─────────────────────────────────
let _popoverActivo = null;

async function verEvidencia(btn, idcompromiso, mes, anio) {
  // Cerrar cualquier popover abierto
  cerrarPopover();

  // Consultar versiones disponibles
  let versiones = [];
  try {
    const res  = await fetch(`/admin/compromisos/versiones/${idcompromiso}?mes=${mes}&anio=${anio}`);
    const json = await res.json();
    console.log('Respuesta del servidor:', json);
    if (!json.success) { showToast('Error al cargar versiones', 'error'); return; }
    versiones = json.versiones;
    console.log('Versiones encontradas:', versiones.length, versiones);
  } catch (error) {
    console.error('Error al cargar versiones:', error);
    showToast('Error de conexión', 'error');
    return;
  }

  // Si solo hay una versión → abrir directo sin popover
  if (versiones.length === 1) {
    console.log('Abriendo versión única:', versiones[0].id_evidencia);
    window.open(`/admin/compromisos/ver-version/${versiones[0].id_evidencia}`, '_blank');
    return;
  }
  
  console.log('Mostrando popover con', versiones.length, 'versiones');

  // Si hay varias → mostrar popover
  const popover = document.createElement('div');
  popover.className = 'versiones-popover';
  popover.id        = 'versionesPopover';

  const header = `
    <div class="versiones-popover__header">
      <span>Versiones de evidencia</span>
      <button onclick="cerrarPopover()" class="versiones-popover__close">
        <i data-feather="x" style="width:13px;height:13px;"></i>
      </button>
    </div>`;

  const items = versiones.map(v => `
    <div class="versiones-popover__item">
      <div class="versiones-popover__info">
        <span class="versiones-popover__version">
          v${v.version}
          ${v.es_ultima_version ? '<span class="versiones-popover__badge">actual</span>' : ''}
        </span>
        <span class="versiones-popover__nombre" title="${v.nombre_archivo}">
          ${v.nombre_archivo}
        </span>
        <span class="versiones-popover__fecha">${v.fecha_subida}</span>
      </div>
      <div class="versiones-popover__acciones">
        <a href="/admin/compromisos/ver-version/${v.id_evidencia}"
           target="_blank"
           class="versiones-popover__btn versiones-popover__btn--ver"
           title="Ver en nueva pestaña">
          <i data-feather="eye" style="width:13px;height:13px;"></i>
        </a>
        <a href="/admin/compromisos/descargar-version/${v.id_evidencia}"
           class="versiones-popover__btn versiones-popover__btn--dl"
           title="Descargar">
          <i data-feather="download" style="width:13px;height:13px;"></i>
        </a>
      </div>
    </div>`).join('');

  popover.innerHTML = header + `<div class="versiones-popover__list">${items}</div>`;

  // Posicionar junto al botón
  document.body.appendChild(popover);
  feather.replace();

  const rect = btn.getBoundingClientRect();
  const scrollY = window.scrollY;
  popover.style.top  = (rect.bottom + scrollY + 6) + 'px';
  popover.style.left = Math.max(8, rect.left - popover.offsetWidth + rect.width) + 'px';

  _popoverActivo = popover;

  // Cerrar al click fuera
  setTimeout(() => {
    document.addEventListener('click', _cerrarPopoverFuera);
  }, 0);
}

function cerrarPopover() {
  const existing = document.getElementById('versionesPopover');
  if (existing) existing.remove();
  _popoverActivo = null;
  document.removeEventListener('click', _cerrarPopoverFuera);
}

function _cerrarPopoverFuera(e) {
  const pop = document.getElementById('versionesPopover');
  if (pop && !pop.contains(e.target)) cerrarPopover();
}


// ── MODAL: EDITAR COMPROMISO ─────────────────────────────
let _editComp = {};

function abrirEditarCompromiso(ds) {
  cerrarPopover();

  _editComp = {
    id:   ds.comp,
    mes:  ds.mes,
    anio: ds.anio,
  };

  // Campos read-only
  document.getElementById('editComp_nombre').value      = ds.nombre      || '';
  document.getElementById('editComp_entidad').value     = ds.entidad     || '';
  document.getElementById('editComp_descripcion').value = ds.descripcion || '';

  // Campos editables
  document.getElementById('editComp_observaciones').value = ds.observaciones || '';
  document.getElementById('editComp_supervisor').value    = ds.idusuario     || '';

  // Estado evidencia
  const divCon = document.getElementById('editComp_conEvidencia');
  const divSin = document.getElementById('editComp_sinEvidencia');

  if (ds.tieneEvidencia === 'true') {
    const urlVer       = `/admin/compromisos/ver-evidencia/${ds.comp}?mes=${ds.mes}&anio=${ds.anio}`;
    const urlDescargar = `/admin/compromisos/descargar/${ds.comp}?mes=${ds.mes}&anio=${ds.anio}`;

    document.getElementById('editComp_nombreArchivo').textContent = ds.nombreArchivo || 'Archivo cargado';
    document.getElementById('editComp_btnVer').href       = urlVer;
    document.getElementById('editComp_btnDescargar').href = urlDescargar;

    divCon.style.display = 'flex';
    divSin.style.display = 'none';
  } else {
    divCon.style.display = 'none';
    divSin.style.display = 'flex';
  }

  // Limpiar archivo previo
  document.getElementById('editComp_archivo').value                     = '';
  document.getElementById('editComp_archivoSeleccionado').style.display = 'none';
  document.getElementById('editComp_archivoLabel').textContent           = '';

  // Limpiar estado
  const estado = document.getElementById('editComp_estado');
  estado.style.display = 'none';
  estado.className     = 'comp-estado-msg';
  estado.textContent   = '';

  abrirModal('modalEditarCompromiso');
  feather.replace();
}

function cerrarEditarCompromiso() {
  cerrarModal('modalEditarCompromiso');
}

function limpiarArchivoEditar() {
  document.getElementById('editComp_archivo').value                     = '';
  document.getElementById('editComp_archivoSeleccionado').style.display = 'none';
  document.getElementById('editComp_archivoLabel').textContent           = '';
}

async function guardarEditarCompromiso() {
  const estado = document.getElementById('editComp_estado');
  estado.style.display = 'block';
  estado.className     = 'comp-estado-msg comp-estado-loading';
  estado.textContent   = 'Guardando...';

  const supervisor    = document.getElementById('editComp_supervisor').value;
  const observaciones = document.getElementById('editComp_observaciones').value;
  const archivo       = document.getElementById('editComp_archivo').files[0];
  const errores       = [];

  // 1) Guardar supervisor + observaciones
  try {
    const r = await fetch('/admin/compromisos/guardar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify({
        idcompromiso:  _editComp.id,
        idusuario:     supervisor    || null,
        observaciones: observaciones || '',
        mes:           _editComp.mes,
        anio:          _editComp.anio,
      }),
    });
    if (!r.ok) errores.push('datos');
  } catch {
    errores.push('datos');
  }

  // 2) Subir archivo si hay uno nuevo
  if (archivo) {
    try {
      const fd = new FormData();
      fd.append('archivo',      archivo);
      fd.append('idcompromiso', _editComp.id);
      fd.append('mes',          _editComp.mes);
      fd.append('anio',         _editComp.anio);
      const r = await fetch('/admin/compromisos/subir-evidencia', {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: fd,
      });
      const json = await r.json();
      if (!r.ok || !json.success) errores.push('evidencia');
    } catch {
      errores.push('evidencia');
    }
  }

  // Resultado
  if (errores.length === 0) {
    estado.className   = 'comp-estado-msg comp-estado-ok';
    estado.textContent = '✅ Guardado correctamente';
    setTimeout(() => { cerrarEditarCompromiso(); location.reload(); }, 1000);
  } else {
    estado.className   = 'comp-estado-msg comp-estado-error';
    estado.textContent = '⚠️ Error al guardar: ' + errores.join(', ');
  }
}


// ── INIT ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  feather.replace();

  document.getElementById('modalEditarCompromiso').addEventListener('click', function (e) {
    if (e.target === this) cerrarEditarCompromiso();
  });

  document.getElementById('editComp_archivo').addEventListener('change', function () {
    if (this.files && this.files[0]) {
      document.getElementById('editComp_archivoLabel').textContent          = this.files[0].name;
      document.getElementById('editComp_archivoSeleccionado').style.display = 'flex';
      feather.replace();
    }
  });
});