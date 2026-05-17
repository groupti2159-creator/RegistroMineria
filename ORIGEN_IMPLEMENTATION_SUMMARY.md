# Implementación de Campo "Origen" en Desvíos Ambientales

## Resumen
Se ha implementado exitosamente el campo "Origen" en el sistema de Desvíos Ambientales. Los usuarios ahora pueden seleccionar el origen de cada reporte (RAC, INSPECCION, o EVENTO DE ALTO RIESGO).

## Cambios Realizados

### 1. Base de Datos

#### Tabla `tbl_registro`
- **Cambio**: Se agregó la columna `idorigen` (INT, DEFAULT 1)
- **Posición**: Después de la columna `ubicacion`
- **Constraint**: Se agregó clave foránea a `tbl_origen(idorigen)`
- **Script**: `add_origen_to_registro.py`

#### Tabla `tbl_origen` (ya existía)
- Contiene 3 registros activos:
  - ID 1: RAC
  - ID 2: INSPECCION
  - ID 3: EVENTO DE ALTO RIESGO (EAP)

### 2. Stored Procedures

#### `sp_crearregistro`
- **Cambio**: Se agregó parámetro `p_idorigen INT` al final
- **Acción**: Inserta el valor de `idorigen` en la tabla `tbl_registro`
- **Default**: Si no se proporciona origen, usa 1 (RAC)

#### `sp_actualizarregistro`
- **Cambio**: Se agregó parámetro `p_idorigen INT` al final
- **Acción**: Actualiza el valor de `idorigen` en la tabla `tbl_registro`
- **Default**: Si no se proporciona origen, usa 1 (RAC)

#### `sp_detalleregistro`
- **Cambio**: Se agregó `idorigen` y `origen_nombre` al SELECT
- **Join**: Se agregó LEFT JOIN con `tbl_origen`
- **Acción**: Retorna el ID y nombre del origen en los detalles del registro

### 3. Backend (Python/Flask)

#### `routes/desvios_ambientales.py`

**Función `get_maestros()`**
- Ya estaba configurada para obtener orígenes de la base de datos
- Query: `SELECT * FROM tbl_origen WHERE activo = 1 ORDER BY nombre`

**Función `crear_registro()`**
- **Cambio**: Se agregó parámetro `origen` al llamar a `sp_crearregistro`
- **Línea**: Se pasa `int(request.form['origen']) if request.form.get('origen') else 1`
- **Acción**: Captura el valor del dropdown y lo envía al SP

**Función `editar_registro()`**
- **Cambio**: Se agregó parámetro `origen` al llamar a `sp_actualizarregistro`
- **Línea**: Se pasa `int(request.form['origen']) if request.form.get('origen') else 1`
- **Acción**: Captura el valor del dropdown y lo envía al SP

### 4. Frontend (HTML/JavaScript)

#### `templates/desvios_ambientales/desvios.html`

**Modal "Crear Reporte"**
- **Ubicación**: Entre UBICACIÓN y DESCRIPCIÓN
- **Campo**: `<select name="origen" class="form-select" required>`
- **Opciones**: Se generan dinámicamente desde `{% for o in origenes %}`
- **Validación**: Campo requerido

**Modal "Editar Reporte"**
- **Ubicación**: Entre UBICACIÓN y DESCRIPCIÓN
- **Campo**: `<select name="origen" id="edit_origen" class="form-select" required>`
- **Opciones**: Se generan dinámicamente desde `{% for o in origenes %}`
- **Validación**: Campo requerido

#### `static/js/desvios_ambientales/desvios.js`

**Función `editarRegistro()`**
- **Cambio**: Se agregó línea para poblar el campo `edit_origen`
- **Línea**: `setVal('edit_origen', r.idorigen);`
- **Acción**: Cuando se abre el modal de edición, carga el origen actual del registro

## Flujo de Datos

### Crear Reporte
1. Usuario abre modal "Nuevo Reporte Ambiental"
2. Completa todos los campos incluyendo "ORIGEN"
3. Hace clic en "Guardar Reporte"
4. JavaScript captura el formulario con AJAX
5. Backend recibe `request.form['origen']`
6. Se llama a `sp_crearregistro` con el parámetro `idorigen`
7. El SP inserta el registro con el origen especificado
8. Se retorna el ID del nuevo registro

### Editar Reporte
1. Usuario hace clic en "Editar" en la tabla
2. Se carga el modal "Editar Reporte"
3. JavaScript obtiene los detalles del registro via `sp_detalleregistro`
4. El campo `edit_origen` se puebla con el valor actual
5. Usuario puede cambiar el origen si lo desea
6. Hace clic en "Actualizar Reporte"
7. Backend recibe `request.form['origen']`
8. Se llama a `sp_actualizarregistro` con el nuevo `idorigen`
9. El SP actualiza el registro

### Ver Detalle
1. Usuario hace clic en "Ver Detalle"
2. Se llama a `sp_detalleregistro`
3. El SP retorna `idorigen` y `origen_nombre`
4. Se muestra en el modal de detalle (si se agrega a la UI)

## Validación

✓ Columna `idorigen` existe en `tbl_registro`
✓ Tabla `tbl_origen` tiene 3 registros activos
✓ `sp_crearregistro` acepta parámetro `idorigen`
✓ `sp_actualizarregistro` acepta parámetro `idorigen`
✓ `sp_detalleregistro` retorna `idorigen`
✓ Dropdown en modal "Crear" muestra opciones
✓ Dropdown en modal "Editar" muestra opciones
✓ Valores se guardan correctamente en la base de datos

## Archivos Modificados

1. `routes/desvios_ambientales.py` - Backend
2. `templates/desvios_ambientales/desvios.html` - Frontend HTML
3. `static/js/desvios_ambientales/desvios.js` - Frontend JavaScript

## Archivos de Migración (Scripts)

1. `add_origen_to_registro.py` - Agrega columna y actualiza SPs
2. `update_sp_detalle.py` - Actualiza sp_detalleregistro
3. `verificar_origen.py` - Verifica datos en tbl_origen
4. `check_registro_schema.py` - Verifica esquema de tbl_registro
5. `test_origen_integration.py` - Test de integración

## Próximos Pasos (Opcional)

1. Agregar el campo `origen_nombre` al modal de detalle para mostrar el nombre del origen
2. Agregar filtro por origen en la tabla de registros
3. Agregar estadísticas por origen
4. Agregar validación adicional en el frontend

## Notas

- El campo "Origen" es obligatorio en ambos modales (Crear y Editar)
- Si no se proporciona un origen, se usa por defecto el ID 1 (RAC)
- Los orígenes se cargan dinámicamente desde la base de datos
- Solo se muestran orígenes activos (`activo = 1`)
- El campo se posiciona entre UBICACIÓN y DESCRIPCIÓN como se solicitó
