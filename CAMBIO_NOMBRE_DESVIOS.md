# Cambio de Nombre: Desvios Ambientales → Desvios Ssoma

## Cambios Realizados

Se ha cambiado el nombre de "Desvios Ambientales" a "Desvios Ssoma" en toda la interfaz.

### Archivo Modificado

**`templates/desvios_ambientales/desvios.html`**

### Cambios Específicos

1. **Título de la página**
   - ANTES: `{% block title %}Desvíos Ambientales — ecoSupervisor{% endblock %}`
   - DESPUÉS: `{% block title %}Desvios Ssoma — ecoSupervisor{% endblock %}`

2. **Encabezado de la página**
   - ANTES: `{% block page_title %}Desvíos Ambientales{% endblock %}`
   - DESPUÉS: `{% block page_title %}Desvios Ssoma{% endblock %}`

3. **Título principal**
   - ANTES: `<h2 class="section-title">Desvíos <span class="text-green">Ambientales</span></h2>`
   - DESPUÉS: `<h2 class="section-title">Desvios <span class="text-green">Ssoma</span></h2>`

4. **Subtítulo**
   - ANTES: `<p class="section-sub">Gestión y seguimiento de reportes ambientales</p>`
   - DESPUÉS: `<p class="section-sub">Gestión y seguimiento de reportes Ssoma</p>`

5. **Botón principal**
   - ANTES: `<strong>Nuevo Reporte Ambiental</strong>`
   - DESPUÉS: `<strong>Nuevo Reporte Ssoma</strong>`

6. **Modal "Registrar Nuevo Reporte"**
   - ANTES: `<p class="modal-eyebrow">Desvíos Ambientales</p>`
   - DESPUÉS: `<p class="modal-eyebrow">Desvios Ssoma</p>`

7. **Modal "Editar Reporte"**
   - ANTES: `<p class="modal-eyebrow">Desvíos Ambientales</p>`
   - DESPUÉS: `<p class="modal-eyebrow">Desvios Ssoma</p>`

8. **Modal "Detalle del Reporte"**
   - ANTES: `<p class="modal-eyebrow">Desvíos Ambientales</p>`
   - DESPUÉS: `<p class="modal-eyebrow">Desvios Ssoma</p>`

9. **Modal "Validar Imágenes de Levantamiento"**
   - ANTES: `<p class="modal-eyebrow">Desvíos Ambientales</p>`
   - DESPUÉS: `<p class="modal-eyebrow">Desvios Ssoma</p>`

## Lugares Donde Aparece el Cambio

- ✓ Título del navegador
- ✓ Encabezado de la página
- ✓ Título principal de la sección
- ✓ Subtítulo descriptivo
- ✓ Botón "Nuevo Reporte Ssoma"
- ✓ Modal de crear reporte
- ✓ Modal de editar reporte
- ✓ Modal de detalle del reporte
- ✓ Modal de validar imágenes

## Verificación

✓ Todos los cambios se han aplicado correctamente
✓ No hay más ocurrencias de "Desvíos Ambientales"
✓ El nombre ahora es "Desvios Ssoma" en toda la interfaz

## Próximos Pasos

1. **Reinicia la aplicación** (si está corriendo)
2. **Abre** `http://127.0.0.1:8080/admin/desvios/registrar`
3. **Verifica que todos los textos muestren "Desvios Ssoma"**

## Conclusión

✓ El cambio de nombre se ha completado exitosamente
✓ La interfaz ahora muestra "Desvios Ssoma" en lugar de "Desvios Ambientales"
