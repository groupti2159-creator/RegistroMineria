// ════════════════════════════════════════════════════════
//  ecoSupervisor — Gestión de Aguas / reporte_ana.js
// ════════════════════════════════════════════════════════

let _anaEditId = null;

// ── CÁLCULO EN TIEMPO REAL ───────────────────────────────
function calcularANA() {
  const ini = parseFloat(document.getElementById('ana_cont_ini').value);
  const fin = parseFloat(document.getElementById('ana_cont_fin').value);
  const volEl    = document.getElementById('ana_volumen');
  const caudalEl = document.getElementById('ana_caudal');

  if (!isNaN(ini) && !isNaN(fin) && fin >= ini) {
    const vol    = +(fin - ini).toFixed(4);
    const caudal = +(vol / 86400).toFixed(9);
    volEl.value    = vol;
    caudalEl.value = caudal;
  } else {
    volEl.value    = '';
    caudalEl.value = '';
  }
}


// ── MODAL ────────────────────────────────────────────────
function abrirModalANA() {
  _anaEditId = null;
  document.getElementById('modalANA-titulo').textContent = 'Nuevo Reporte ANA';
  document.getElementById('ana_fecha').value     = '';
  document.getElementById('ana_tiempo').value    = '24 horas';
  document.getElementById('ana_cont_ini').value  = '';
  document.getElementById('ana_cont_fin').value  = '';
  document.getElementById('ana_volumen').value   = '';
  document.getElementById('ana_caudal').value    = '';
  _limpiarEstado();
  abrirModal('modalANA');
  feather.replace();
}

function cerrarModalANA() {
  cerrarModal('modalANA');
  _anaEditId = null;
}

function _limpiarEstado() {
  const el = document.getElementById('anaEstado');
  el.style.display = 'none';
  el.className     = 'comp-estado-msg';
  el.textContent   = '';
}

function _setEstado(msg, tipo) {
  const el = document.getElementById('anaEstado');
  el.style.display = 'block';
  el.className     = 'comp-estado-msg comp-estado-' + tipo;
  el.textContent   = msg;
}


// ── GUARDAR (crear o editar) ─────────────────────────────
async function guardarANA() {
  const fecha   = document.getElementById('ana_fecha').value;
  const tiempo  = document.getElementById('ana_tiempo').value;
  const contIni = document.getElementById('ana_cont_ini').value;
  const contFin = document.getElementById('ana_cont_fin').value;

  if (!fecha || !contIni || !contFin) {
    _setEstado('⚠️ Fecha, Contómetro Inicial y Final son obligatorios', 'error');
    return;
  }

  _setEstado('Guardando...', 'loading');

  const fd = new FormData();
  fd.append('fecha',               fecha);
  fd.append('tiempo_operacion',    tiempo || '24 horas');
  fd.append('contometro_inicial',  contIni);
  fd.append('contometro_final',    contFin);

  const url = _anaEditId
    ? `/admin/ana/editar/${_anaEditId}`
    : '/admin/ana/crear';

  try {
    const r    = await fetch(url, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: fd,
    });
    const json = await r.json();

    if (json.success) {
      _setEstado('✅ Guardado correctamente', 'ok');
      setTimeout(() => { cerrarModalANA(); location.reload(); }, 900);
    } else {
      _setEstado('⚠️ Error: ' + (json.error || 'desconocido'), 'error');
    }
  } catch {
    _setEstado('⚠️ Error de conexión', 'error');
  }
}


// ── EDITAR ───────────────────────────────────────────────
async function editarRegistro(id) {
  try {
    const res  = await fetch(`/admin/ana/detalle/${id}`);
    const data = await res.json();
    if (data.error) { showToast(data.error, 'error'); return; }

    _anaEditId = id;
    document.getElementById('modalANA-titulo').textContent = `Editar Reporte ANA #${id}`;
    document.getElementById('ana_fecha').value    = data.fecha             || '';
    document.getElementById('ana_tiempo').value   = data.tiempooperacion   || '24 horas';
    document.getElementById('ana_cont_ini').value = data.contometroinicial ?? '';
    document.getElementById('ana_cont_fin').value = data.contometrofinal   ?? '';
    calcularANA();
    _limpiarEstado();
    abrirModal('modalANA');
    feather.replace();
  } catch {
    showToast('Error al cargar reporte', 'error');
  }
}


// ── ELIMINAR ─────────────────────────────────────────────
async function eliminarRegistro(id) {
  if (!confirm('¿Eliminar este reporte? No se puede deshacer.')) return;
  try {
    const res  = await fetch(`/admin/ana/eliminar/${id}`,
      { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    const json = await res.json();
    if (json.success) {
      showToast('Reporte eliminado', 'success');
      setTimeout(() => location.reload(), 800);
    } else {
      showToast(json.error || 'Error al eliminar', 'error');
    }
  } catch {
    showToast('Error de conexión', 'error');
  }
}


// ── FILTROS ──────────────────────────────────────────────
function aplicarFiltros() {
  const q  = document.getElementById('inputBuscar').value.toLowerCase();
  const fi = document.getElementById('filtroFechaIni').value;
  const ff = document.getElementById('filtroFechaFin').value;
  const tbody = document.getElementById('tbody-ana');
  if (!tbody) return;
  let v = 0;
  tbody.querySelectorAll('tr[data-fecha]').forEach(tr => {
    const ok = (!q  || tr.textContent.toLowerCase().includes(q))
            && (!fi || tr.dataset.fecha >= fi)
            && (!ff || tr.dataset.fecha <= ff);
    tr.style.display = ok ? '' : 'none';
    if (ok) v++;
  });
  document.getElementById('contadorRegistros').textContent = v + ' registros';
  document.getElementById('contadorTabla').textContent     = v + ' registros';
}

function limpiarFiltros() {
  document.getElementById('inputBuscar').value    = '';
  document.getElementById('filtroFechaIni').value = '';
  document.getElementById('filtroFechaFin').value = '';
  aplicarFiltros();
}


// ── TOAST ────────────────────────────────────────────────
// showToast global de main.js
function _cerrarModalLocal() { cerrarModalANA(); }


// ── INIT ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  feather.replace();
  document.getElementById('modalANA').addEventListener('click', function (e) {
    if (e.target === this) cerrarModalANA();
  });
});