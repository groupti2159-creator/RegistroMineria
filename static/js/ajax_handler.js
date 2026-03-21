// ═══════════════════════════════════════════════════════
// AJAX HANDLER - Actualización sin recargar página
// ═══════════════════════════════════════════════════════

// ── FUNCIONES AUXILIARES ──

/**
 * Mostrar notificación temporal
 */
function mostrarNotificacion(mensaje, tipo = 'success') {
  const notif = document.createElement('div');
  notif.className = `ajax-notificacion notif-${tipo}`;
  
  const icon = tipo === 'success' ? 'check-circle' : 
               tipo === 'error' ? 'x-circle' : 'info';
  
  notif.innerHTML = `
    <i data-feather="${icon}"></i>
    <span>${mensaje}</span>
  `;
  
  document.body.appendChild(notif);
  
  // Inicializar icono de Feather
  if (typeof feather !== 'undefined') {
    feather.replace();
  }
  
  // Auto-remover después de 4 segundos
  setTimeout(() => {
    notif.classList.add('fade-out');
    setTimeout(() => notif.remove(), 300);
  }, 4000);
}

/**
 * Recargar tabla de registros
 */
async function recargarTabla() {
  const tbody = document.querySelector('.data-table tbody');
  if (!tbody) {
    console.warn('No se encontró tbody de la tabla');
    return;
  }
  
  // Mostrar loading
  const loadingRow = document.createElement('tr');
  loadingRow.innerHTML = `
    <td colspan="20" style="text-align:center;padding:2rem;color:var(--text-secondary)">
      <i data-feather="loader" style="width:24px;height:24px;animation:spin 1s linear infinite"></i>
      <span style="margin-left:0.5rem">Actualizando...</span>
    </td>
  `;
  tbody.innerHTML = '';
  tbody.appendChild(loadingRow);
  
  if (typeof feather !== 'undefined') {
    feather.replace();
  }
  
  try {
    // Obtener URL actual con parámetros
    const url = new URL(window.location.href);
    url.searchParams.set('ajax', '1');
    
    const response = await fetch(url.toString());
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const html = await response.text();
    
    // Extraer solo el tbody del HTML
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    const newTbody = doc.querySelector('.data-table tbody');
    
    if (newTbody && newTbody.children.length > 0) {
      tbody.innerHTML = newTbody.innerHTML;
      
      // Reinicializar iconos de Feather
      if (typeof feather !== 'undefined') {
        feather.replace();
      }
      
      console.log('Tabla actualizada correctamente');
    } else {
      throw new Error('No se encontró contenido de tabla en la respuesta');
    }
  } catch (error) {
    console.error('Error recargando tabla:', error);
    tbody.innerHTML = `
      <tr>
        <td colspan="20" style="text-align:center;padding:2rem;color:var(--text-red)">
          <i data-feather="alert-circle"></i>
          <span style="margin-left:0.5rem">Error al actualizar. Por favor recarga la página.</span>
        </td>
      </tr>
    `;
    if (typeof feather !== 'undefined') {
      feather.replace();
    }
  }
}

/**
 * Deshabilitar botón durante operación
 */
function deshabilitarBoton(button, textoLoading = 'Procesando...') {
  if (!button) return null;
  
  const textoOriginal = button.textContent;
  button.disabled = true;
  button.dataset.textoOriginal = textoOriginal;
  button.innerHTML = `<i data-feather="loader" style="width:16px;height:16px;animation:spin 1s linear infinite"></i> ${textoLoading}`;
  
  if (typeof feather !== 'undefined') {
    feather.replace();
  }
  
  return textoOriginal;
}

/**
 * Rehabilitar botón
 */
function habilitarBoton(button) {
  if (!button) return;
  
  button.disabled = false;
  const textoOriginal = button.dataset.textoOriginal || 'Enviar';
  button.textContent = textoOriginal;
  delete button.dataset.textoOriginal;
}

// ── INTERCEPTAR FORMULARIO DE CREAR ──

document.addEventListener('DOMContentLoaded', function() {
  const modalCrear = document.getElementById('modalCrear');
  if (!modalCrear) return;
  
  const formCrear = modalCrear.querySelector('form');
  if (!formCrear) return;
  
  console.log('Interceptando formulario de crear con AJAX');
  
  formCrear.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const submitBtn = this.querySelector('button[type="submit"]');
    
    // Deshabilitar botón
    deshabilitarBoton(submitBtn, 'Creando...');
    
    try {
      const response = await fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      
      const contentType = response.headers.get('content-type');
      
      // Si el servidor retorna JSON
      if (contentType && contentType.includes('application/json')) {
        const result = await response.json();
        
        if (result.success) {
          // Cerrar modal
          modalCrear.style.display = 'none';
          
          // Mostrar notificación
          mostrarNotificacion(result.message || 'Registro creado exitosamente', 'success');
          
          // Recargar tabla
          await recargarTabla();
          
          // Limpiar formulario y previews
          if (typeof resetFormCrear === 'function') resetFormCrear();
          else {
            this.reset();
            const previews = this.querySelectorAll('.preview-container');
            previews.forEach(p => p.innerHTML = '');
          }
        } else {
          mostrarNotificacion(result.error || 'Error al crear registro', 'error');
        }
      } else {
        // Si el servidor retorna HTML (comportamiento antiguo)
        // Significa que funcionó y redirigió
        mostrarNotificacion('Registro creado exitosamente', 'success');
        await recargarTabla();
        modalCrear.style.display = 'none';
        if (typeof resetFormCrear === 'function') resetFormCrear();
        else this.reset();
      }
    } catch (error) {
      console.error('Error:', error);
      mostrarNotificacion('Error de conexión. Intenta nuevamente.', 'error');
    } finally {
      // Rehabilitar botón
      habilitarBoton(submitBtn);
    }
  });
});

// ── INTERCEPTAR FORMULARIO DE EDITAR ──

document.addEventListener('DOMContentLoaded', function() {
  const modalEditar = document.getElementById('modalEditar');
  if (!modalEditar) return;
  
  const formEditar = modalEditar.querySelector('form');
  if (!formEditar) return;
  
  console.log('Interceptando formulario de editar con AJAX');
  
  formEditar.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    // Agregar imágenes a eliminar (gestionadas por desvios.js)
    if (typeof imagenesEditarEliminar !== 'undefined') {
      formData.set('imagenes_eliminar', imagenesEditarEliminar.join(','));
    }
    
    const submitBtn = this.querySelector('button[type="submit"]');
    
    // Deshabilitar botón
    deshabilitarBoton(submitBtn, 'Guardando...');
    
    try {
      // Construir URL con el ID del registro
      let actionUrl = this.action;
      if (!actionUrl || actionUrl === window.location.href) {
        // Si no tiene action, construir desde el ID del formulario
        const registroId = formData.get('registro_id') || formData.get('idregistro');
        actionUrl = `/admin/editar_registro/${registroId}`;
      }
      
      const response = await fetch(actionUrl, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        const result = await response.json();
        
        if (result.success) {
          modalEditar.style.display = 'none';
          mostrarNotificacion(result.message || 'Registro actualizado exitosamente', 'success');
          await recargarTabla();
        } else {
          mostrarNotificacion(result.error || 'Error al actualizar registro', 'error');
        }
      } else {
        // Comportamiento antiguo (HTML)
        mostrarNotificacion('Registro actualizado exitosamente', 'success');
        await recargarTabla();
        modalEditar.style.display = 'none';
      }
    } catch (error) {
      console.error('Error:', error);
      mostrarNotificacion('Error de conexión. Intenta nuevamente.', 'error');
    } finally {
      habilitarBoton(submitBtn);
    }
  });
});

// ── INTERCEPTAR FORMULARIO DE VALIDAR IMÁGENES ──

document.addEventListener('DOMContentLoaded', function() {
  const formValidar = document.getElementById('formValidar');
  if (!formValidar) return;

  // Capturar qué botón se clickeó antes del submit
  let decisionClickeada = null;
  formValidar.querySelectorAll('button[type="submit"][name="decision"]').forEach(btn => {
    btn.addEventListener('click', function() {
      decisionClickeada = this.value;
    });
  });

  formValidar.addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    // Agregar manualmente el valor del botón clickeado
    if (decisionClickeada) {
      formData.set('decision', decisionClickeada);
    }

    const submitBtn = this.querySelector('button[type="submit"]');
    deshabilitarBoton(submitBtn, 'Validando...');

    try {
      const response = await fetch(formValidar.action, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });

      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        const result = await response.json();

        if (result.success) {
          if (typeof cerrarModalValidar === 'function') cerrarModalValidar();
          else {
            const modalValidar = document.getElementById('modalValidar');
            if (modalValidar) modalValidar.style.display = 'none';
          }
          mostrarNotificacion(result.message || 'Imágenes validadas exitosamente', 'success');
          await recargarTabla();
        } else {
          mostrarNotificacion(result.error || 'Error al validar imágenes', 'error');
        }
      } else {
        mostrarNotificacion('Imágenes validadas exitosamente', 'success');
        await recargarTabla();
        if (typeof cerrarModalValidar === 'function') cerrarModalValidar();
      }
    } catch (error) {
      console.error('Error:', error);
      mostrarNotificacion('Error de conexión. Intenta nuevamente.', 'error');
    } finally {
      habilitarBoton(submitBtn);
      decisionClickeada = null;
    }
  });
});

// ── INTERCEPTAR FORMULARIO DE SUBIR IMÁGENES (SUPERVISOR) ──

document.addEventListener('DOMContentLoaded', function() {
  const formSubir = document.getElementById('formSubir');
  if (!formSubir) return;
  
  console.log('Interceptando formulario de subir con AJAX');
  
  formSubir.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const submitBtn = this.querySelector('button[type="submit"]');
    
    // Deshabilitar botón
    deshabilitarBoton(submitBtn, 'Subiendo...');
    
    try {
      const response = await fetch(this.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });
      
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        const result = await response.json();
        
        if (result.success) {
          const modalSubir = document.getElementById('modalSubir');
          if (modalSubir) modalSubir.style.display = 'none';
          
          mostrarNotificacion(result.message || 'Imágenes subidas exitosamente', 'success');
          await recargarTabla();
          this.reset();
        } else {
          mostrarNotificacion(result.error || 'Error al subir imágenes', 'error');
        }
      } else {
        // Comportamiento antiguo
        mostrarNotificacion('Imágenes subidas exitosamente', 'success');
        await recargarTabla();
        const modalSubir = document.getElementById('modalSubir');
        if (modalSubir) modalSubir.style.display = 'none';
        this.reset();
      }
    } catch (error) {
      console.error('Error:', error);
      mostrarNotificacion('Error de conexión. Intenta nuevamente.', 'error');
    } finally {
      habilitarBoton(submitBtn);
    }
  });
});

console.log('✅ AJAX Handler cargado correctamente');
