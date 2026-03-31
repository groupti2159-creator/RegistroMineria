const TIPOS   = ['efluentes','ptard','ptap'];
const TITULOS = {efluentes:'Efluentes', ptard:'PTARD', ptap:'PTAP'};
let tipoActual = 'efluentes';

function cambiarTipo(val) {
  tipoActual = val;
  TIPOS.forEach(t => {
    document.getElementById('tabla-'+t).style.display = (t===val) ? '' : 'none';
  });
  document.getElementById('tituloTabla').textContent = TITULOS[val];
  document.getElementById('btnExportar').href = `/admin/aguas/exportar?tipo=${val}`;
  aplicarFiltros();
  feather.replace();
}

function aplicarFiltros() {
  const q  = document.getElementById('inputBuscar').value.toLowerCase();
  const fi = document.getElementById('filtroFechaIni').value;
  const ff = document.getElementById('filtroFechaFin').value;
  const tbody = document.getElementById('tbody-'+tipoActual);
  if (!tbody) return;
  let v = 0;
  tbody.querySelectorAll('tr[data-search]').forEach(tr => {
    const ok = (!q  || tr.dataset.search.includes(q))
            && (!fi || tr.dataset.fecha >= fi)
            && (!ff || tr.dataset.fecha <= ff);
    tr.style.display = ok ? '' : 'none';
    if (ok) v++;
  });
  document.getElementById('contadorRegistros').textContent = v + ' registros';
  document.getElementById('contadorTabla').textContent     = v + ' registros';
}

function limpiarFiltros() {
  document.getElementById('inputBuscar').value = '';
  document.getElementById('filtroFechaIni').value = '';
  document.getElementById('filtroFechaFin').value = '';
  aplicarFiltros();
}

function abrirModal(tipo) {
  document.getElementById('selectTipo').value = tipo;
  cambiarTipo(tipo);
  document.getElementById('modal-'+tipo).style.display = 'flex';
  try { feather.replace(); } catch(e) {}
}

function cerrarModal(id) {
  document.getElementById(id).style.display = 'none';
}

let editandoId   = null;
let editandoTipo = null;

async function editarRegistro(tipo, id) {
  try {
    const res  = await fetch(`/admin/aguas/detalle/${tipo}/${id}`);
    const data = await res.json();
    if (data.error) { showToast(data.error, 'error'); return; }

    editandoId   = id;
    editandoTipo = tipo;

    const form = document.querySelector(`#modal-${tipo} form`);
    form.action = `/admin/aguas/editar/${tipo}/${id}`;

    form.querySelector('[name=fecha]').value      = data.fecha      || '';
    form.querySelector('[name=efluente]').value   = data.idefluente || '';
    form.querySelector('[name=supervisor]').value = data.idusuario  || '';
    form.querySelector('[name=caudal_max]').value     = data.caudalmax     ?? '';
    form.querySelector('[name=caudal_tratado]').value = data.caudaltratado ?? '';

    if (tipo === 'efluentes') {
      form.querySelector('[name=tss]').value    = data.tss    ?? '';
      form.querySelector('[name=cu_tot]').value = data.cutot  ?? '';
      form.querySelector('[name=pb_tot]').value = data.pbtot  ?? '';
      form.querySelector('[name=zn_tot]').value = data.zntot  ?? '';
      form.querySelector('[name=fe_tot]').value = data.fetot  ?? '';
      form.querySelector('[name=as_tot]').value = data.astot  ?? '';
      form.querySelector('[name=ph_lab]').value = data.phlab  ?? '';
      form.querySelector('[name=tss_lmp]').value    = data.tss_lmp   ?? '';
      form.querySelector('[name=cu_lmp]').value     = data.cu_lmp    ?? '';
      form.querySelector('[name=pb_lmp]').value     = data.pb_lmp    ?? '';
      form.querySelector('[name=zn_lmp]').value     = data.zn_lmp    ?? '';
      form.querySelector('[name=fe_lmp]').value     = data.fe_lmp    ?? '';
      form.querySelector('[name=as_lmp]').value     = data.as_lmp    ?? '';
      form.querySelector('[name=cn_lmp]').value     = data.cn_lmp    ?? '';
      form.querySelector('[name=cr_vi_lmp]').value  = data.crvi_lmp  ?? '';
      form.querySelector('[name=ph_min]').value     = data.phmin     ?? '';
      form.querySelector('[name=ph_max]').value     = data.phmax     ?? '';
    } else {
      form.querySelector('[name=turbidez]').value = data.turbidez ?? '';
      form.querySelector('[name=cloro]').value    = data.cloro    ?? '';
      form.querySelector('[name=od]').value       = data.od       ?? '';
      form.querySelector('[name=ph]').value       = data.ph       ?? '';
      form.querySelector('[name=turbidez_lmp]').value = data.turbidez_lmp ?? '';
      form.querySelector('[name=cloro_lmp]').value    = data.cloro_lmp    ?? '';
      form.querySelector('[name=od_lmp]').value       = data.od_lmp       ?? '';
      form.querySelector('[name=ph1_lmp]').value      = data.ph1_lmp      ?? '';
      form.querySelector('[name=ph2_lmp]').value      = data.ph2_lmp      ?? '';
      if (tipo === 'ptard') {
        form.querySelector('[name=dbo]').value     = data.dbo     ?? '';
        form.querySelector('[name=dqo]').value     = data.dqo     ?? '';
        form.querySelector('[name=dbo_lmp]').value = data.dbo_lmp ?? '';
        form.querySelector('[name=dqo_lmp]').value = data.dqo_lmp ?? '';
      }
    }

    const titulo = form.closest('.modal-box').querySelector('.modal-title');
    titulo.textContent = `Editar Registro — ${tipo.toUpperCase()} #${id}`;

    form.onsubmit = async function(e) {
      e.preventDefault();
      const fd  = new FormData(form);
      const res = await fetch(form.action, {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'},
        body: fd
      });
      const json = await res.json();
      if (json.success) {
        showToast('Registro actualizado', 'success');
        cerrarModal(`modal-${tipo}`);
        setTimeout(() => location.reload(), 800);
      } else {
        showToast(json.error || 'Error al actualizar', 'error');
      }
    };

    document.getElementById(`modal-${tipo}`).style.display = 'flex';
    feather.replace();
  } catch(e) {
    showToast('Error al cargar registro', 'error');
  }
}

async function eliminarRegistro(tipo, id) {
  if (!confirm('¿Eliminar este registro? Esta acción no se puede deshacer.')) return;
  try {
    const res  = await fetch('/admin/aguas/eliminar/'+tipo+'/'+id,
      {method:'POST', headers:{'X-Requested-With':'XMLHttpRequest'}});
    const json = await res.json();
    if (json.success) {
      showToast('Registro eliminado','success');
      setTimeout(() => location.reload(), 800);
    } else {
      showToast(json.error || 'Error al eliminar','error');
    }
  } catch(e) { showToast('Error de conexión','error'); }
}

function showToast(msg, type) {
  const d = document.createElement('div');
  d.className = 'alert alert-'+type;
  d.style.cssText = 'position:fixed;top:1rem;right:1rem;z-index:9999;min-width:280px';
  d.innerHTML = '<span>'+msg+'</span>'
    + '<button onclick="this.parentElement.remove()"><i data-feather="x"></i></button>';
  document.body.appendChild(d);
  feather.replace();
  setTimeout(() => d.remove(), 4000);
}

['modal-efluentes','modal-ptard','modal-ptap'].forEach(id => {
  document.getElementById(id).addEventListener('click', function(e) {
    if (e.target === this) cerrarModal(id);
  });
});

document.addEventListener('DOMContentLoaded', () => {
  aplicarFiltros();
  feather.replace();
});
