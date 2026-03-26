# Mejora: Actualización en Tiempo Real sin Recargar Página

## 🎯 PROBLEMA IDENTIFICADO

**Síntoma**: Al subir imágenes o cambiar estados, es necesario presionar F5 o actualizar manualmente para ver los cambios.

**Causa**: El formulario de subir imágenes del supervisor no estaba cargando el archivo `ajax_handler.js`, que intercepta los formularios y los envía vía AJAX.

---

## ✅ SOLUCIÓN IMPLEMENTADA

### Cambio Realizado:

**Archivo**: `templates/desvios_ambientales/supervisor_desvios.html`

Se agregó la carga del script `ajax_handler.js` ANTES de `desvios.js`:

```html
{% block scripts %}
<script>
const DETALLE_URL_BASE = "{{ url_for('supervisor.detalle_registro', rid='PLACEHOLDER') }}".replace('PLACEHOLDER','');
const SUBIR_URL_BASE   = "{{ url_for('supervisor.subir_levantamiento', rid='PLACEHOLDER') }}".replace('PLACEHOLDER','');
const IS_ADMIN = false;
</script>
<!-- ✅ NUEVO: Cargar ajax_handler.js primero -->
<script src="{{ url_for('static', filename='js/desvios_ambientales/ajax_handler.js') }}"></script>
<script src="{{ url_for('static', filename='js/desvios_ambientales/desvios.js') }}"></script>
{% endblock %}
```

---

## 🔧 CÓMO FUNCIONA

### 1. Interceptación de Formularios

El archivo `ajax_handler.js` intercepta automáticamente los siguientes formularios:

- **Crear registro** (`#modalCrear form`)
- **Editar registro** (`#modalEditar form`)
- **Subir imágenes** (`#formSubir`) ← Este era el que faltaba
- **Validar imágenes** (`#formValidar`)

### 2. Proceso AJAX

Cuando se envía un formulario:

```javascript
1. Prevenir recarga de página (e.preventDefault())
2. Crear FormData con los datos del formulario
3. Enviar vía fetch() con header 'X-Requested-With': 'XMLHttpRequest'
4. Esperar respuesta JSON del servidor
5. Mostrar notificación de éxito/error
6. Recargar solo la tabla (sin recargar toda la página)
7. Cerrar el modal automáticamente
```

### 3. Notificaciones Visuales

Se muestran notificaciones temporales en la esquina superior derecha:

- ✅ **Verde**: Operación exitosa
- ❌ **Rojo**: Error
- ℹ️ **Azul**: Información

Las notificaciones desaparecen automáticamente después de 4 segundos.

### 4. Actualización de Tabla

La función `recargarTabla()` actualiza solo el contenido de la tabla sin recargar toda la página:

```javascript
async function recargarTabla() {
  // 1. Mostrar loading en la tabla
  // 2. Hacer fetch a la URL actual con parámetro ?ajax=1
  // 3. Extraer solo el <tbody> del HTML
  // 4. Reemplazar el tbody actual
  // 5. Reinicializar iconos de Feather
}
```

---

## 📊 BENEFICIOS

### Antes (sin AJAX):
- ❌ Recarga completa de página (lento)
- ❌ Pérdida de scroll position
- ❌ Pérdida de filtros aplicados
- ❌ Experiencia de usuario interrumpida
- ❌ Consumo innecesario de ancho de banda

### Después (con AJAX):
- ✅ Actualización instantánea (rápido)
- ✅ Mantiene scroll position
- ✅ Mantiene filtros aplicados
- ✅ Experiencia fluida y moderna
- ✅ Solo actualiza lo necesario

---

## 🧪 PRUEBAS

### Prueba 1: Subir Imágenes (Supervisor)

1. Ir a `/supervisor/desvios`
2. Click en botón "Subir levantamiento" de un registro Pendiente
3. Seleccionar 1-5 imágenes
4. Click en "Subir Imágenes"
5. **Resultado esperado**:
   - Modal se cierra automáticamente
   - Aparece notificación verde "X imagen(es) subida(s) exitosamente"
   - Tabla se actualiza mostrando el nuevo estado "En Proceso"
   - NO se recarga toda la página

### Prueba 2: Crear Registro (Admin)

1. Ir a `/admin/registrar`
2. Click en "Nuevo Reporte"
3. Llenar formulario y subir evidencias
4. Click en "Guardar Reporte"
5. **Resultado esperado**:
   - Modal se cierra
   - Notificación verde "Registro creado exitosamente"
   - Nuevo registro aparece en la tabla
   - NO se recarga la página

### Prueba 3: Editar Registro (Admin)

1. Click en botón "Editar" de un registro
2. Modificar algún campo (ej: descripción, estado)
3. Click en "Guardar Cambios"
4. **Resultado esperado**:
   - Modal se cierra
   - Notificación verde "Registro actualizado exitosamente"
   - Cambios se reflejan en la tabla
   - NO se recarga la página

### Prueba 4: Validar Imágenes (Admin)

1. Click en "Ver detalle" de un registro con levantamientos pendientes
2. Click en "Validar Conjunto de Imágenes"
3. Aprobar o rechazar
4. **Resultado esperado**:
   - Modal se cierra
   - Notificación verde "Imágenes validadas exitosamente"
   - Estado del registro se actualiza en la tabla
   - NO se recarga la página

---

## 🔍 DEBUGGING

### Ver logs en consola del navegador:

```javascript
// Al cargar la página, deberías ver:
✅ AJAX Handler cargado correctamente
Interceptando formulario de crear con AJAX
Interceptando formulario de editar con AJAX
Interceptando formulario de subir con AJAX
```

### Si no funciona:

1. **Abrir DevTools** (F12)
2. **Ir a Console**
3. **Buscar errores en rojo**
4. **Verificar que se carguen los scripts**:
   ```javascript
   // En Console, ejecutar:
   console.log(typeof recargarTabla); // Debe mostrar "function"
   console.log(typeof mostrarNotificacion); // Debe mostrar "function"
   ```

### Errores comunes:

**Error**: `recargarTabla is not defined`
- **Causa**: `ajax_handler.js` no se cargó
- **Solución**: Verificar que el script esté en la ruta correcta

**Error**: `Cannot read property 'classList' of null`
- **Causa**: El modal no existe en el DOM
- **Solución**: Verificar que el ID del modal sea correcto

**Error**: `Failed to fetch`
- **Causa**: Problema de red o servidor caído
- **Solución**: Verificar que el servidor Flask esté corriendo

---

## 🎨 PERSONALIZACIÓN

### Cambiar duración de notificaciones:

En `ajax_handler.js`, línea ~25:

```javascript
// Cambiar de 4000ms (4 segundos) a otro valor
setTimeout(() => {
  notif.classList.add('fade-out');
  setTimeout(() => notif.remove(), 300);
}, 4000); // ← Cambiar aquí
```

### Cambiar posición de notificaciones:

En `main.css`, buscar `.ajax-notificacion`:

```css
.ajax-notificacion {
  position: fixed;
  top: 20px;      /* ← Cambiar posición vertical */
  right: 20px;    /* ← Cambiar posición horizontal */
  /* ... */
}
```

### Cambiar colores de notificaciones:

En `main.css`:

```css
.ajax-notificacion.notif-success {
  background: #10b981; /* ← Verde */
  color: white;
}

.ajax-notificacion.notif-error {
  background: #ef4444; /* ← Rojo */
  color: white;
}

.ajax-notificacion.notif-info {
  background: #3b82f6; /* ← Azul */
  color: white;
}
```

---

## 📝 NOTAS TÉCNICAS

### Compatibilidad con Backend

El backend debe retornar JSON cuando detecta una petición AJAX:

```python
# En routes/supervisor.py
if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    return jsonify({
        'success': True,
        'message': f'{saved} imagen(es) subida(s) exitosamente'
    })
```

**Estado actual**: ✅ Ya implementado en:
- `routes/desvios_ambientales.py` (crear, editar, eliminar, validar)
- `routes/supervisor.py` (subir levantamiento)

### Fallback para navegadores antiguos

Si el navegador no soporta `fetch()`, el formulario se enviará de forma tradicional (con recarga de página). Esto garantiza compatibilidad con navegadores antiguos.

### Manejo de errores

El sistema maneja automáticamente:
- Errores de red (timeout, sin conexión)
- Errores del servidor (500, 404)
- Errores de validación (400)
- Respuestas inesperadas

En todos los casos, se muestra una notificación de error al usuario.

---

## 🚀 PRÓXIMAS MEJORAS OPCIONALES

### 1. WebSockets para actualizaciones en tiempo real

Implementar WebSockets para que múltiples usuarios vean cambios en tiempo real sin necesidad de recargar:

```python
# Usando Flask-SocketIO
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('registro_actualizado')
def handle_registro_actualizado(data):
    emit('actualizar_tabla', data, broadcast=True)
```

### 2. Optimistic UI Updates

Actualizar la UI inmediatamente antes de recibir respuesta del servidor:

```javascript
// Actualizar tabla optimistamente
actualizarFilaOptimista(registroId, nuevosDatos);

// Luego enviar al servidor
await fetch(...);

// Si falla, revertir cambios
```

### 3. Caché de imágenes

Implementar caché de imágenes para evitar recargarlas:

```javascript
const imageCache = new Map();

function cargarImagen(url) {
  if (imageCache.has(url)) {
    return imageCache.get(url);
  }
  // Cargar y cachear
}
```

### 4. Paginación AJAX

Implementar paginación sin recargar página:

```javascript
document.querySelectorAll('.pagination-number').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    e.preventDefault();
    await cargarPagina(btn.dataset.page);
  });
});
```

---

**Fecha**: 2026-03-25
**Versión**: 1.0
**Estado**: ✅ Implementado y funcionando
