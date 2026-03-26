# Revisión del Módulo de Desvíos Ambientales

## 🔍 ANÁLISIS COMPLETO - Posibles Errores y Mejoras

---

## ⚠️ PROBLEMAS CRÍTICOS DETECTADOS

### 1. **Inconsistencia en Actualización de Estados Atrasados**
**Ubicación**: `routes/desvios_ambientales.py` y `routes/supervisor.py`

**Problema**: 
- El SP `sp_actualizarestadosatrasados` se llama en múltiples lugares (dashboard, registrar, desvios supervisor)
- Si un usuario no visita estas páginas, los estados NO se actualizan automáticamente
- Los registros pueden permanecer "Pendientes" aunque ya estén vencidos

**Impacto**: Alto - Los reportes atrasados no se marcan correctamente

**Solución Recomendada**:
```python
# Opción 1: Crear un middleware que ejecute el SP en cada request
@app.before_request
def actualizar_estados_antes_de_request():
    if request.endpoint and 'static' not in request.endpoint:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'sp_actualizarestadosatrasados')
        mysql.connection.commit()
        cur.close()

# Opción 2: Crear un job programado (cron) que ejecute cada hora
# Opción 3: Usar un trigger en MySQL que se ejecute automáticamente
```

---

### 2. **Lógica de Cambio de Estado en Edición**
**Ubicación**: `routes/desvios_ambientales.py` líneas 228-280

**Problema**:
- La lógica para cambiar entre Pendiente/Atrasado al editar es compleja
- Solo funciona si el usuario selecciona específicamente esos estados
- Si el usuario selecciona "En Proceso" pero la fecha está vencida, no se marca como atrasado

**Código Actual**:
```python
# Si el estado seleccionado es Atrasado o Pendiente, verificar la fecha
if estado_nuevo in [estados.get('Pendiente'), estados.get('Atrasado')]:
    if fecha_ejec_date >= fecha_actual:
        estado_nuevo = estados.get('Pendiente')
    else:
        estado_nuevo = estados.get('Atrasado')
```

**Problema**: ¿Qué pasa si el estado es "En Proceso" pero la fecha de ejecución ya pasó?

**Solución Recomendada**:
```python
# Validar SIEMPRE que si la fecha de ejecución pasó y el estado es Pendiente, cambiar a Atrasado
# Esto debería hacerse en el stored procedure, no en Python
```

---

### 3. **Permisos de Subida de Imágenes**
**Ubicación**: `routes/supervisor.py` líneas 82-95

**Problema**:
- El código permite subir levantamientos solo en estado "Pendiente"
- Pero la validación está comentada
- La tabla permite subir en "Pendiente" O "Atrasado" según `tabla_registros.html` línea 48

**Código Actual**:
```python
# NOTA: Actualmente solo se permite subir imágenes cuando el estado es PENDIENTE
# Si el cliente quiere permitir subir más imágenes después de aprobar,
# descomentar la siguiente validación y ajustar la lógica del stored procedure
```

**Inconsistencia**: La UI permite subir en "Atrasado" pero el comentario dice solo "Pendiente"

**Solución**: Aclarar y documentar cuándo se puede subir imágenes

---

### 4. **Límite de 5 Imágenes No Validado Correctamente**
**Ubicación**: `routes/supervisor.py` líneas 97-102

**Problema**:
```python
cur.execute("SELECT COUNT(*) AS cnt FROM tbl_imagenregistro WHERE idregistro=%s AND idtipoimagen=2 AND idestadoimagen != 3", (rid,))
cnt_row = cur.fetchone()
existing = cnt_row['cnt'] if cnt_row else 0

for f in files:
    if existing + saved >= 5:
        break
```

**Problema**: 
- Solo valida para levantamientos (idtipoimagen=2)
- No valida para evidencias (idtipoimagen=1)
- El límite de 5 puede superarse si se suben evidencias y levantamientos por separado

**Solución**: Validar límites por tipo de imagen

---

## ⚡ PROBLEMAS DE RENDIMIENTO

### 5. **Consultas Múltiples en Cada Request**
**Ubicación**: `routes/desvios_ambientales.py` función `registrar()`

**Problema**:
```python
# Se ejecuta SP_ActualizarEstadosAtrasados en CADA carga de página
cur = mysql.connection.cursor()
sp_exec(cur, 'sp_actualizarestadosatrasados')
mysql.connection.commit()
cur.close()

# Luego se consultan TODOS los registros para obtener estados únicos
cur = mysql.connection.cursor()
todos_registros = sp_exec(cur, 'sp_listarregistros', (None,))
cur.close()
```

**Impacto**: 
- Si hay 1000 registros, se cargan todos en memoria solo para extraer estados únicos
- El SP de actualización se ejecuta en cada request, incluso si no hay cambios

**Solución**:
```python
# Opción 1: Cachear los estados únicos
# Opción 2: Crear un SP específico para obtener solo estados únicos
# Opción 3: Ejecutar actualización de estados solo cada X minutos (cache)
```

---

### 6. **Ordenamiento en Python en Lugar de SQL**
**Ubicación**: `routes/desvios_ambientales.py` líneas 88-90

**Problema**:
```python
orden_estados = {'Pendiente':1,'Atrasado':2,'Asignado':3,'En Proceso':4,'Enviado':5,'En Revision':6,'Culminado':7,'Rechazado':8,'Cerrado':9}
registros_ordenados = sorted(registros, key=lambda x: orden_estados.get(x.get('estado',''), 999))
```

**Impacto**: Se ordenan registros en Python después de traerlos de la BD

**Solución**: Ordenar en el stored procedure usando CASE WHEN

---

## 🐛 BUGS POTENCIALES

### 7. **Manejo de CCTA Responsable con Valor 0**
**Ubicación**: `routes/desvios_ambientales.py` líneas 273-274

**Problema**:
```python
int(request.form['ccta_responsable']) if request.form.get('ccta_responsable','').strip() not in ('','0','None') else 0
```

**Problema**: 
- Si el usuario selecciona CCTA con ID 0, se trata como "sin asignar"
- Pero 0 podría ser un ID válido en la base de datos

**Solución**: Usar NULL en lugar de 0 para "sin asignar"

---

### 8. **Falta Validación de Fechas**
**Ubicación**: `routes/desvios_ambientales.py` función `crear_registro()`

**Problema**:
- No se valida que `fecha_ejecucion` sea posterior a `fecha_inicio`
- No se valida que las fechas sean válidas
- Permite crear registros con fechas en el futuro lejano

**Solución**: Agregar validaciones de negocio

---

### 9. **Eliminación en Cascada Manual**
**Ubicación**: `routes/desvios_ambientales.py` líneas 323-327

**Problema**:
```python
cur.execute("DELETE FROM tbl_historialaprobacion WHERE idregistro=%s", (rid,))
cur.execute("DELETE FROM tbl_notificacion WHERE idregistro=%s", (rid,))
cur.execute("DELETE FROM tbl_registro WHERE idregistro=%s", (rid,))
```

**Problema**: 
- Si falla alguna eliminación, puede quedar inconsistente
- No usa transacciones explícitas
- Falta eliminar de `tbl_imagenregistro`

**Solución**: Usar stored procedure con transacción o configurar CASCADE en BD

---

### 10. **Notificaciones a TODOS los Supervisores**
**Ubicación**: `routes/desvios_ambientales.py` líneas 213-219

**Problema**:
```python
cur.execute("SELECT ur.idusuariorol FROM tbl_usuariorol ur JOIN tbl_roles r ON r.idroles=ur.idroles WHERE r.nombrerol IN ('Supervisor','Trabajador')")
sups = cur.fetchall()
for s in sups:
    sp_exec(cur, 'sp_crearnotificacion', (s['idusuariorol'], f'Nuevo reporte {codigo} creado', 'info', rid))
```

**Problema**: 
- Se notifica a TODOS los supervisores y trabajadores
- No se filtra por área o proyecto
- Puede generar spam de notificaciones

**Solución**: Notificar solo al supervisor del área responsable

---

## 📊 MEJORAS DE UX/UI

### 11. **Paginación Pierde Filtros**
**Ubicación**: `templates/shared/tabla_registros.html` líneas 60-62

**Problema**:
```html
<a href="?estado={{ estado_filter }}&page={{ p }}" class="pagination-number">{{ p }}</a>
```

**Problema**: Solo mantiene el filtro de estado, pierde el filtro de personal

**Solución**:
```html
<a href="?estado={{ estado_filter }}&personal={{ personal_filter }}&page={{ p }}">
```

---

### 12. **Sin Confirmación al Eliminar**
**Ubicación**: JavaScript (no visible en archivos revisados)

**Problema**: Probablemente falta confirmación visual antes de eliminar

**Solución**: Agregar modal de confirmación con detalles del registro

---

## 🔒 SEGURIDAD

### 13. **Falta Validación de Permisos en Detalle**
**Ubicación**: `routes/supervisor.py` función `detalle_registro()`

**Problema**:
- Un supervisor puede ver el detalle de CUALQUIER registro
- No se valida que el registro pertenezca a su área

**Solución**: Validar que el supervisor solo vea registros de su área

---

### 14. **Inyección SQL Potencial**
**Ubicación**: `routes/desvios_ambientales.py` línea 325

**Problema**:
```python
cur.execute("DELETE FROM tbl_registro WHERE idregistro=%s", (rid,))
```

**Estado**: Correcto (usa parámetros)

**Pero**: Revisar que TODOS los queries usen parámetros, no concatenación

---

## ✅ RECOMENDACIONES GENERALES

### Prioridad Alta:
1. ✅ Implementar actualización automática de estados (middleware o cron)
2. ✅ Corregir lógica de eliminación en cascada
3. ✅ Validar permisos por área en supervisor
4. ✅ Optimizar consultas (evitar cargar todos los registros)

### Prioridad Media:
5. ✅ Agregar validaciones de fechas
6. ✅ Mejorar sistema de notificaciones (filtrar por área)
7. ✅ Cachear estados únicos
8. ✅ Ordenar en SQL en lugar de Python

### Prioridad Baja:
9. ✅ Mejorar UX de paginación
10. ✅ Agregar confirmaciones de eliminación
11. ✅ Documentar límites de imágenes

---

## 📝 PRÓXIMOS PASOS SUGERIDOS

1. **Crear un job programado** para actualizar estados atrasados cada hora
2. **Refactorizar la función de edición** para simplificar la lógica de estados
3. **Agregar tests unitarios** para validar la lógica de cambio de estados
4. **Optimizar stored procedures** para incluir ordenamiento y filtros
5. **Implementar soft delete** en lugar de eliminación física
6. **Agregar logs de auditoría** para cambios de estado

---

**Fecha de Revisión**: 2026-03-25
**Revisor**: Kiro AI Assistant
**Módulo**: Desvíos Ambientales
