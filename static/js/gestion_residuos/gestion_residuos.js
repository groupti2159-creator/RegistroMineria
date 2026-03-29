'use strict';

const PLANT_COLUMN_MAP = {
  'SUNEC': 'sunec',
  'CORI PUNO': 'coripuno',
  'ANTIOQUIA': 'antioquia',
  'PARCOY': 'parcoy',
  'SANTA MARÍA': 'smaria',
};

/* ── Estado ── */
const vals = {};
let timer = null;
let modoEdicion = false;
let idEditando  = null;

/* ── Referencias DOM ── */
const overlay        = document.getElementById('modal-overlay');
const detalleOverlay = document.getElementById('modal-detalle-overlay');

/* ══════════════════════════════════════
   MODAL REGISTRO — Abrir / Cerrar
══════════════════════════════════════ */
function abrirModalNuevo() {
  modoEdicion = false;
  idEditando  = null;
  Object.keys(vals).forEach(k => delete vals[k]);
  document.querySelectorAll('.plant-input').forEach(el => {
    el.value = '';
    el.classList.remove('has-val');
  });
  document.querySelectorAll('.sec-total').forEach(el => {
    el.textContent = '0 ' + (el.closest('.sec')?.dataset.unit || '');
  });
  setText('generacion-t', '0.000 t');
  setText('footer-kg', '0 Kg');
  document.querySelector('.modal-title').textContent = 'Registro RRSS diario';
  setText('btn-save', 'Guardar');
  const hoy = new Date().toISOString().split('T')[0];
  document.getElementById('input-fecha').value = hoy;
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function cerrar() {
  overlay.classList.remove('open');
  document.body.style.overflow = '';
}

document.getElementById('btn-open')?.addEventListener('click', abrirModalNuevo);
document.getElementById('btn-close')?.addEventListener('click', cerrar);
document.getElementById('btn-cancel')?.addEventListener('click', cerrar);
overlay?.addEventListener('click', e => { if (e.target === overlay) cerrar(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') { cerrar(); cerrarDetalle(); } });

/* ── Toggle sección ── */
function toggleSec(id) {
  document.getElementById('sec-' + id)?.classList.toggle('open');
}

/* ── Al escribir en una planta ── */
function onInput(el) {
  const sid = el.dataset.sec;
  const idx = parseInt(el.dataset.idx);
  if (!vals[sid]) vals[sid] = [0, 0, 0, 0];
  vals[sid][idx] = parseFloat(el.value) || 0;
  el.classList.toggle('has-val', vals[sid][idx] > 0);
  clearTimeout(timer);
  timer = setTimeout(calcularEnPython, 300);
}

/* ── Calcular ── */
async function calcularEnPython() {
  try {
    const res = await fetch('/admin/rrss/calcular', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ valores: vals }),
    });
    renderizar(await res.json());
  } catch { calcularLocal(); }
}

function renderizar(data) {
  for (const [sid, info] of Object.entries(data.secciones || {}))
    setText('tot-' + sid, fmt(info.total) + ' ' + info.unit);
  setText('generacion-t', (data.generacion_t || '0.000') + ' t');
  setText('footer-kg', fmt(data.total_kg || 0) + ' Kg (sin aceites)');
}

function calcularLocal() {
  let totalKg = 0;
  document.querySelectorAll('.sec').forEach(sec => {
    const sid  = sec.dataset.id;
    const unit = sec.dataset.unit;
    const suma = (vals[sid] || [0,0,0,0]).reduce((a,b) => a+b, 0);
    setText('tot-' + sid, fmt(suma) + ' ' + unit);
    if (unit === 'Kg') totalKg += suma;
  });
  setText('generacion-t', (totalKg/1000).toFixed(3) + ' t');
  setText('footer-kg', fmt(totalKg) + ' Kg (sin aceites)');
}

/* ── Guardar / Actualizar ── */
document.getElementById('btn-save')?.addEventListener('click', async () => {
  const fecha = document.getElementById('input-fecha')?.value;
  if (!fecha) { alert('Selecciona una fecha.'); return; }
  const genT = document.getElementById('generacion-t')?.textContent?.replace(' t','').trim() || '0';
  const url  = modoEdicion ? '/admin/rrss/editar/' + idEditando : '/admin/rrss/guardar';

  try {
    const res  = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fecha, valores: vals, generacion_t: parseFloat(genT) }),
    });
    const data = await res.json();
    if (data.success) { cerrar(); location.reload(); }
    else alert('Error: ' + (data.error || 'desconocido') + '\n\n' + (data.detail || ''));
  } catch { alert('Error de conexión.'); }
});

/* ══════════════════════════════════════
   MODAL DETALLE — Ver más
══════════════════════════════════════ */
function cerrarDetalle() {
  detalleOverlay?.classList.remove('open');
  document.body.style.overflow = '';
}

document.getElementById('btn-close-detalle')?.addEventListener('click', cerrarDetalle);
document.getElementById('btn-cancel-detalle')?.addEventListener('click', cerrarDetalle);
detalleOverlay?.addEventListener('click', e => { if (e.target === detalleOverlay) cerrarDetalle(); });

function verDetalle(r) {
  const fechaRaw = r.fecha ? r.fecha.substring(0, 10) : null;
  const fecha = fechaRaw ? fechaRaw.split('-').reverse().join('/') : '—';
  setText('detalle-fecha-titulo', 'Registro del ' + fecha);
  setText('detalle-gen-t', parseFloat(r.generacion_t || 0).toFixed(3) + ' t');

  // Thead dinámico — las plantas pueden variar por sección, usamos las estándar en el header
  // y mostramos el label de planta en cada fila
  const tbody = document.getElementById('detalle-tbody');
  tbody.innerHTML = '';
  let totalGenKg = 0;

  const plantDefaults = window.PLANTS || ['SUNEC', 'CORI PUNO', 'ANTIOQUIA', 'PARCOY'];
  const sectionPlantLists = (window.SECTIONS || []).map(sec => sec.plants || plantDefaults);
  const maxCols = Math.max(plantDefaults.length, ...sectionPlantLists.map(list => list.length));

  const thead = document.getElementById('detalle-thead');
  thead.innerHTML = '';
  const headerRow = document.createElement('tr');
  headerRow.innerHTML = `
    <th class="col-sticky">Sección</th>
    ${Array.from({ length: maxCols }, (_, i) => `<th style="text-align:right">Planta ${i + 1}</th>`).join('')}
    <th style="text-align:right">Total</th>
    <th>Unidad</th>
  `;
  thead.appendChild(headerRow);

  (window.SECTIONS || []).forEach(sec => {
    const sid = sec.id;
    const plantList = sec.plants || plantDefaults;
    const cols = sec.col_keys || plantList.map(p => `${sid}_${PLANT_COLUMN_MAP[p] || p.toLowerCase().replace(/\s+/g,'_')}`);
    const values = cols.map(c => parseFloat(r[c] || 0));
    const total = parseFloat(r[sid + '_total'] || 0);
    if (sec.en_total) totalGenKg += total;

    const cells = [];
    for (let i = 0; i < maxCols; i++) {
      const label = plantList[i] || '';
      const value = i < values.length ? values[i] : null;
      cells.push(`
        <td style="text-align:right">
          ${label ? `<span style="display:block;font-size:.7rem;color:var(--text-muted);margin-bottom:2px">${label}</span>` : ''}
          ${value !== null ? fmt(value) : ''}
        </td>
      `);
    }

    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="col-sticky" style="font-weight:600">${sec.label}</td>
      ${cells.join('')}
      <td class="col-subtotal" style="text-align:right;font-weight:600">${fmt(total)}</td>
      <td style="color:var(--text-muted);font-size:.8rem">${sec.unit}</td>
    `;
    tbody.appendChild(tr);
  });

  const trTotal = document.createElement('tr');
  trTotal.style.cssText = 'background:var(--bg-card);font-weight:700;border-top:2px solid var(--border)';
  trTotal.innerHTML = `
    <td class="col-sticky" style="font-weight:700;color:var(--green)">TOTAL GENERAL</td>
    <td colspan="${plantDefaults.length}"></td>
    <td class="col-subtotal" style="text-align:right;color:var(--green)">${fmt(totalGenKg)}</td>
    <td style="color:var(--text-muted);font-size:.8rem">Kg</td>
  `;
  tbody.appendChild(trTotal);

  detalleOverlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

/* ══════════════════════════════════════
   EDITAR
══════════════════════════════════════ */
function editarRegistro(r) {
  modoEdicion = true;
  idEditando  = r.idgeneracion;

  Object.keys(vals).forEach(k => delete vals[k]);

  const plantDefaults = window.PLANTS || ['SUNEC', 'CORI PUNO', 'ANTIOQUIA', 'PARCOY'];
  (window.SECTIONS || []).forEach(sec => {
    const sid = sec.id;
    const plantList = sec.plants || plantDefaults;
    const cols = sec.col_keys || plantList.map(p => `${sid}_${PLANT_COLUMN_MAP[p] || p.toLowerCase().replace(/\s+/g,'_')}`);
    vals[sid] = cols.map(c => parseFloat(r[c] || 0));
  });

  document.querySelectorAll('.plant-input').forEach(el => {
    const sid = el.dataset.sec;
    const idx = parseInt(el.dataset.idx);
    const val = vals[sid]?.[idx] || 0;
    el.value = val > 0 ? val : '';
    el.classList.toggle('has-val', val > 0);
  });

  const fecha = r.fecha ? r.fecha.substring(0, 10) : '';
  document.getElementById('input-fecha').value = fecha;
  document.querySelector('.modal-title').textContent = 'Editar registro RRSS';
  setText('btn-save', 'Actualizar');

  calcularEnPython();
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

/* ══════════════════════════════════════
   ELIMINAR
══════════════════════════════════════ */
async function eliminarRegistro(id) {
  if (!confirm('¿Eliminar este registro? Esta acción no se puede deshacer.')) return;
  try {
    const res  = await fetch('/admin/rrss/eliminar/' + id, { method: 'POST' });
    const data = await res.json();
    if (data.success) location.reload();
    else alert('Error al eliminar: ' + data.error);
  } catch { alert('Error de conexión.'); }
}

/* ── Utilidades ── */
function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function fmt(n) {
  return (Math.round(n * 100) / 100).toLocaleString('es-PE', {
    minimumFractionDigits: 0, maximumFractionDigits: 2,
  });
}
