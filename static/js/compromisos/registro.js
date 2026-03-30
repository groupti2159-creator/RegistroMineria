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
function showToast(msg, type) {
  const d = document.createElement('div');
  d.className = 'alert alert-' + (type === 'error' ? 'error' : type === 'success' ? 'success' : 'info');
  d.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:9999;min-width:280px;';
  d.innerHTML = `<span>${msg}</span>
    <button onclick="this.parentElement.remove()"><i data-feather="x"></i></button>`;
  document.body.appendChild(d);
  feather.replace();
  setTimeout(() => d.remove(), 4000);
}


// ── MODAL: EDITAR COMPROMISO ─────────────────────────────
let _editComp = {};

function abrirEditarCompromiso(ds) {
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

  document.getElementById('modalEditarCompromiso').style.display = 'flex';
  feather.replace();
}

function cerrarEditarCompromiso() {
  document.getElementById('modalEditarCompromiso').style.display = 'none';
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
    estado.className = 'comp-estado-msg comp-estado-ok';
    estado.textContent = '✅ Guardado correctamente';
    setTimeout(() => { cerrarEditarCompromiso(); location.reload(); }, 1000);
  } else {
    estado.className = 'comp-estado-msg comp-estado-error';
    estado.textContent = '⚠️ Error al guardar: ' + errores.join(', ');
  }
}


// ── INIT ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  feather.replace();

  // Cerrar modal al click fuera
  document.getElementById('modalEditarCompromiso').addEventListener('click', function (e) {
    if (e.target === this) cerrarEditarCompromiso();
  });

  // Mostrar nombre de archivo seleccionado
  document.getElementById('editComp_archivo').addEventListener('change', function () {
    if (this.files && this.files[0]) {
      document.getElementById('editComp_archivoLabel').textContent          = this.files[0].name;
      document.getElementById('editComp_archivoSeleccionado').style.display = 'flex';
      feather.replace();
    }
  });
});