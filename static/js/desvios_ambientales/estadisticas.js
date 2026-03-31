// URLS se define inline en el template porque depende de url_for de Jinja2
// CONFIG también se define inline por la misma razón (referencia a URLS)

let tipoActual = null;
let chartModal = null;

function abrirModalEstadistica(tipo) {
  tipoActual = tipo;
  const cfg = CONFIG[tipo];
  document.getElementById('modalTitulo').textContent    = cfg.titulo;
  document.getElementById('modalSubtitulo').textContent = cfg.subtitulo;
  document.getElementById('filtroFechaIni').value = '';
  document.getElementById('filtroFechaFin').value = '';
  abrirModal('modalEstadisticas');
  feather.replace();
  cargarModal();
}

function cerrarModalEstadistica() {
  cerrarModal('modalEstadisticas');
  if (chartModal) { chartModal.destroy(); chartModal = null; }
  document.getElementById('modalContenido').innerHTML = '';
  tipoActual = null;
}

function aplicarFiltro() { cargarModal(); }

function limpiarFiltro() {
  document.getElementById('filtroFechaIni').value = '';
  document.getElementById('filtroFechaFin').value = '';
  cargarModal();
}

async function cargarModal() {
  if (!tipoActual) return;
  const fi = document.getElementById('filtroFechaIni').value;
  const ff = document.getElementById('filtroFechaFin').value;
  let url = URLS[tipoActual];
  const p = new URLSearchParams();
  if (fi) p.set('fecha_ini', fi);
  if (ff) p.set('fecha_fin', ff);
  if (p.toString()) url += '?' + p.toString();
  document.getElementById('modalContenido').innerHTML =
    '<div style="text-align:center;padding:3rem;color:var(--text-muted)">Cargando...</div>';
  try {
    const res  = await fetch(url, { headers: {'X-Requested-With': 'XMLHttpRequest'} });
    const data = await res.json();
    renderModalContenido(CONFIG[tipoActual], data);
  } catch(e) {
    document.getElementById('modalContenido').innerHTML =
      '<div class="alert alert-error">Error: ' + e.message + '</div>';
  }
}

function renderModalContenido(cfg, data) {
  if (chartModal) { chartModal.destroy(); chartModal = null; }
  if (!data || data.length === 0) {
    document.getElementById('modalContenido').innerHTML =
      '<div style="text-align:center;padding:3rem;color:var(--text-muted)"><p>Sin datos para el rango seleccionado</p></div>';
    return;
  }
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  const palette = isDark
    ? ['#60a5fa','#34d399','#fbbf24','#f87171','#a78bfa','#f472b6','#22d3ee','#a3e635','#fb923c','#818cf8']
    : ['#3b82f6','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899','#06b6d4','#84cc16','#f97316','#6366f1'];
  const colores = palette.slice(0, data.length);
  const labels  = data.map(r => r[cfg.labelKey]);
  const valores = data.map(r => r[cfg.valorKey]);
  const chartH  = cfg.isHoriz ? Math.max(data.length * 44 + 60, 200) : 300;
  const thCols  = cfg.cols.map(c => '<th>' + c + '</th>').join('');
  const rows    = data.map(r => '<tr>' + cfg.rowFn(r) + '</tr>').join('');
  let totalRow  = '';
  if (cfg.isHoriz) {
    const totPend = data.reduce((s, r) => s + parseInt(r.pendiente || 0, 10), 0);
    const totAtra = data.reduce((s, r) => s + parseInt(r.atrasado  || 0, 10), 0);
    const tot     = data.reduce((s, r) => s + parseInt(r.cantidad_pendiente || 0, 10), 0);
    totalRow = '<tr style="font-weight:700;border-top:2px solid var(--border)">' +
      '<td>TOTAL GENERAL</td>' +
      '<td style="text-align:center"><span class="estado-badge estado-pendiente">' + totPend + '</span></td>' +
      '<td style="text-align:center"><span class="estado-badge estado-atrasado">'  + totAtra + '</span></td>' +
      '<td style="text-align:center"><span class="cantidad-badge total">'           + tot     + '</span></td></tr>';
  }

  document.getElementById('modalContenido').innerHTML =
    '<div style="padding:1rem 0">' +
    '<div style="height:' + chartH + 'px;margin-bottom:1.5rem"><canvas id="chartModal"></canvas></div>' +
    '<div class="table-wrapper"><table class="data-table"><thead><tr>' + thCols +
    '</tr></thead><tbody>' + rows + totalRow + '</tbody></table></div></div>';

  const scaleMain  = { beginAtZero: true, ticks: { stepSize: 1, color: isDark ? '#a3a3a3' : '#525252' }, grid: { color: isDark ? 'rgba(255,255,255,.08)' : 'rgba(0,0,0,.05)' } };
  const scaleCross = { ticks: { autoSkip: false, maxRotation: cfg.isHoriz ? 0 : 40, color: isDark ? '#a3a3a3' : '#525252' }, grid: { display: false } };

  chartModal = new Chart(document.getElementById('chartModal').getContext('2d'), {
    type: 'bar',
    data: { labels, datasets: [{ data: valores, backgroundColor: colores, borderRadius: 6, borderSkipped: false }] },
    options: {
      indexAxis: cfg.isHoriz ? 'y' : 'x',
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { displayColors: false, callbacks: {
          label: c => (cfg.isHoriz ? 'Pendientes: ' : 'Total: ') + (cfg.isHoriz ? c.parsed.x : c.parsed.y) + ' reportes'
        }}
      },
      scales: {
        x: cfg.isHoriz ? scaleMain : scaleCross,
        y: cfg.isHoriz ? scaleCross : scaleMain
      },
      animation: { duration: 900, easing: 'easeOutQuart' }
    }
  });
}

document.getElementById('modalEstadisticas').addEventListener('click', function(e) {
  if (e.target === this) cerrarModalEstadistica();
});
