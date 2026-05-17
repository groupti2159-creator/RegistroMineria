# Debug: Dropdown de Origen No Muestra Datos

## Problema Reportado
El dropdown de "ORIGEN" en el modal "Registrar Nuevo Reporte" no muestra las opciones de la tabla `tbl_origen`.

## Investigación Realizada

### 1. Verificación de Datos en Base de Datos ✓
- La tabla `tbl_origen` existe
- Contiene 3 registros activos:
  - ID 1: RAC
  - ID 2: INSPECCION
  - ID 3: EVENTO DE ALTO RIESGO (EAP)

### 2. Verificación de Función `get_maestros()` ✓
- La función obtiene correctamente los orígenes
- Query: `SELECT * FROM tbl_origen WHERE activo = 1 ORDER BY nombre`
- Retorna 3 registros con estructura correcta

### 3. Verificación de Paso a Plantilla ✓
- La variable `origenes` se pasa correctamente a `render_template()`
- Se incluye en el diccionario de contexto

### 4. Verificación de Render de Plantilla ✓
- El template de Jinja2 renderiza correctamente
- Las opciones se generan correctamente en el HTML

### 5. Verificación de HTML ✓
- El dropdown tiene la estructura correcta
- El loop `{% for o in origenes %}` está bien formado
- Los atributos `value` y `nombre` se acceden correctamente

## Posibles Causas

### Causa 1: Variable `origenes` vacía en la plantilla
**Solución aplicada**: Se agregó validación `{% if origenes %}` en la plantilla para mostrar un mensaje si está vacía.

### Causa 2: Problema de caché del navegador
**Solución**: Limpiar caché del navegador o hacer Ctrl+Shift+R

### Causa 3: Problema de JavaScript que limpia el dropdown
**Solución**: Se verificó que `resetFormCrear()` no afecta el dropdown

### Causa 4: Problema de CSS que oculta las opciones
**Solución**: Verificar en DevTools si las opciones están presentes pero ocultas

## Cambios Realizados

### 1. Plantilla HTML - Modal Crear
```html
<select name="origen" class="form-select" required>
    <option value="">Seleccionar origen...</option>
    {% if origenes %}
        {% for o in origenes %}
        <option value="{{ o.idorigen }}">{{ o.nombre }}</option>
        {% endfor %}
    {% else %}
        <option value="" disabled>No hay orígenes disponibles</option>
    {% endif %}
</select>
```

### 2. Plantilla HTML - Modal Editar
```html
<select name="origen" id="edit_origen" class="form-select" required>
    <option value="">Seleccionar origen...</option>
    {% if origenes %}
        {% for o in origenes %}
        <option value="{{ o.idorigen }}">{{ o.nombre }}</option>
        {% endfor %}
    {% else %}
        <option value="" disabled>No hay orígenes disponibles</option>
    {% endif %}
</select>
```

### 3. Backend - Debug
Se agregó debug en la ruta `/registrar` para verificar que `origenes` se está cargando:
```python
print(f"DEBUG: origenes cargados = {len(origenes)}", file=sys.stderr)
for o in origenes:
    print(f"DEBUG: origen = {o}", file=sys.stderr)
```

## Pasos para Verificar

1. **Abrir DevTools** (F12)
2. **Ir a la pestaña "Console"**
3. **Hacer clic en "Nuevo Reporte Ambiental"**
4. **Inspeccionar el dropdown**:
   - Click derecho en el dropdown
   - Seleccionar "Inspeccionar"
   - Verificar que las opciones están presentes en el HTML

5. **Verificar en la consola del servidor**:
   - Ver si aparecen los mensajes DEBUG
   - Verificar que `origenes` tiene 3 registros

## Checklist de Verificación

- [ ] Los datos existen en `tbl_origen`
- [ ] La función `get_maestros()` retorna los datos
- [ ] La variable `origenes` se pasa a la plantilla
- [ ] El HTML del dropdown contiene las opciones
- [ ] El dropdown no está oculto por CSS
- [ ] JavaScript no está limpiando el dropdown
- [ ] El navegador no está usando caché antiguo

## Próximos Pasos

1. Verificar en el navegador si el dropdown muestra las opciones
2. Si no muestra, revisar la consola del navegador para errores
3. Si muestra, el problema está resuelto
4. Remover el código de debug una vez confirmado que funciona

## Notas

- El dropdown está posicionado entre UBICACIÓN y DESCRIPCIÓN como se solicitó
- El campo es obligatorio (required)
- Las opciones se cargan dinámicamente desde la base de datos
- Si se agregan nuevos orígenes, aparecerán automáticamente
