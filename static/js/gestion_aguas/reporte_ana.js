// ── Filtros ──────────────────────────────────────────────
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

// ── Modal ────────────────────────────────────────────────
function abrirModal() {
  document.getElementById('modalANA').style.display = 'flex';
  feather.replace();
}

function cerrarModal() {
  const form = document.getElementById('formANA');
  form.reset();
  form.action   = '/admin/ana/crear';
  form.onsubmit = null;
  document.getElementById('modalANA-titulo').textContent = 'Nuevo Reporte ANA';
  document.getElementById('modalANA').style.display = 'none';
}

// ── Editar ───────────────────────────────────────────────
async function editarRegistro(id) {
  try {
    const res  = await fetch(`/admin/ana/detalle/${id}`);
    const data = await res.json();
    if (data.error) { showToast(data.error, 'error'); return; }

    const form = document.getElementById('formANA');
    form.action = `/admin/ana/editar/${id}`;

    form.querySelector('[name=fecha]').value              = data.fecha           || '';
    form.querySelector('[name=tiempo_operacion]').value   = data.tiempooperacion || '';
    form.querySelector('[name=contometro_inicial]').value = data.contometroinicial ?? '';
    form.querySelector('[name=contometro_final]').value   = data.contometrofinal   ?? '';

    document.getElementById('modalANA-titulo').textContent = `Editar Reporte ANA #${id}`;

    form.onsubmit = async function(e) {
      e.preventDefault();
      const fd  = new FormData(form);
      const r   = await fetch(form.action, {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: fd
      });
      const json = await r.json();
      if (json.success) {
        showToast('Reporte actualizado', 'success');
        cerrarModal();
        setTimeout(() => location.reload(), 800);
      } else {
        showToast(json.error || 'Error al actualizar', 'error');
      }
    };

    abrirModal();
  } catch(e) {
    showToast('Error al cargar reporte', 'error');
  }
}

// ── Eliminar ─────────────────────────────────────────────
async function eliminarRegistro(id) {
  if (!confirm('¿Eliminar este reporte? Esta acción no se puede deshacer.')) return;
  try {
    const res  = await fetch(`/admin/ana/eliminar/${id}`,
      { method: 'POST', headers: {'X-Requested-With': 'XMLHttpRequest'} });
    const json = await res.json();
    if (json.success) {
      showToast('Reporte eliminado', 'success');
      setTimeout(() => location.reload(), 800);
    } else {
      showToast(json.error || 'Error al eliminar', 'error');
    }
  } catch(e) {
    showToast('Error de conexión', 'error');
  }
}

// ── Toast ────────────────────────────────────────────────
function showToast(msg, type) {
  const d = document.createElement('div');
  d.className = 'alert alert-' + type;
  d.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:9999;min-width:280px';
  d.innerHTML = `<span>${msg}</span>
    <button onclick="this.parentElement.remove()">
      <i data-feather="x"></i>
    </button>`;
  document.body.appendChild(d);
  feather.replace();
  setTimeout(() => d.remove(), 4000);
}

// ── Cerrar modal al click afuera ─────────────────────────
document.getElementById('modalANA').addEventListener('click', function(e) {
  if (e.target === this) cerrarModal();
});

document.addEventListener('DOMContentLoaded', () => feather.replace());
