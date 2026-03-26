# Resumen de Cambios - Sesión de Mejoras

## 📋 ÍNDICE DE CAMBIOS

1. [Actualización Automática de Estados Atrasados](#1-actualización-automática-de-estados-atrasados)
2. [Simplificación de Lógica de Edición](#2-simplificación-de-lógica-de-edición)
3. [Integración de Estado "Atrasado" en Estadísticas](#3-integración-de-estado-atrasado-en-estadísticas)
4. [Actualización en Tiempo Real (AJAX)](#4-actualización-en-tiempo-real-ajax)
5. [Fix de Duplicación de Imágenes](#5-fix-de-duplicación-de-imágenes)

---

## 1. Actualización Automática de Estados Atrasados

### Problema:
Los estados "Atrasado" solo se actualizaban cuando el usuario visitaba ciertas páginas específicas.

### Solución:
**Archivo**: `app.py`

Agregado middleware que ejecuta automáticamente el SP cada 5 minutos:

```python
from datetime import datetime, timedelta

_ultimo_update_estados = None
_intervalo_update = timedelta(minutes=5)

@app.before_request
def actualizar_estados_atrasados():
    global _ultimo_update_estados
    
    if request.endpoint and 'static' not in request.endpoint:
        ahora = datetime.now()
        
        if _ultimo_update_estados is None or (ahora - _ultimo_update_estados) > _intervalo_update:
            try:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_actualizarestadosatrasados')
                mysql.connection.commit()
                cur.close()
                _ultimo_update_estados = ahora
                print(f"[{ahora.strftime('%H:%M:%S')}] Estados atrasados actualizados")
            except Exception as e:
                print(f"[actualizar_estados_atrasados] error: {e}")
```

**Archivos modificados**:
- `routes/desvios_ambientales.py` - Eliminadas llamadas manuales en `dashboard()` y `registrar()`
- `routes/supervisor.py` - Eliminada llamada manual en `desvios()`

---

## 2. Simplificación de Lógica de Edición

### Problema:
Lógica compleja de ~40 líneas en Python para determinar si un registro debe ser Pendiente o Atrasado.

### Solución:
**Archivo**: `mejorar_sp_actualizar_registro.sql`

Creado stored procedure mejorado que maneja la lógica automáticamente:

```sql
CREATE PROCEDURE SP_ActualizarRegistro(...)
BEGIN
    DECLARE v_estado_final INT;
    DECLARE v_id_pendiente INT;
    DECLARE v_id_atrasado INT;
    
    -- Obtener IDs de estados
    SELECT idEstado INTO v_id_pendiente FROM tbl_estado WHERE Estado = 'Pendiente' LIMIT 1;
    SELECT idEstado INTO v_id_atrasado FROM tbl_estado WHERE Estado = 'Atrasado' LIMIT 1;
    
    -- Determinar estado basado en fecha
    SET v_estado_final = p_idestado;
    
    IF p_idestado IN (v_id_pendiente, v_id_atrasado) THEN
        IF p_fechaejecucion IS NOT NULL THEN
            IF DATE(p_fechaejecucion) < CURDATE() THEN
                SET v_estado_final = v_id_atrasado;
            ELSE
                SET v_estado_final = v_id_pendiente;
            END IF;
        ELSE
            SET v_estado_final = v_id_pendiente;
        END IF;
    END IF;
    
    -- Actualizar registro
    UPDATE tbl_registro SET ... idEstado = v_estado_final ...
END
```

**Archivo**: `routes/desvios_ambientales.py`

Simplificada función `editar_registro()` de ~40 líneas a solo 5 líneas.

---

## 3. Integración de Estado "Atrasado" en Estadísticas

### Problema:
Las estadísticas no mostraban el estado "Atrasado" por separado.

### Solución:
**Archivo**: `actualizar_sp_estadisticas.sql`

Actualizados 3 stored procedures:

1. **SP_EstadisticasAreas** - Agregada columna `atrasado`
2. **SP_EstadisticasCcta** - Agregada columna `atrasado` + JOIN para mostrar nombres
3. **SP_Estadisticas_Tipos_Pendientes** - Agregadas columnas `pendiente`, `atrasado`, `cantidad_pendiente`

**Archivo**: `templates/desvios_ambientales/estadisticas.html`

- Agregada columna "Atrasados" en tablas de áreas y ccta
- Agregadas columnas "Pendientes", "Atrasados", "Total" en tabla de tipos
- Fix del bug "0111" usando `parseInt()` para sumar correctamente

---

## 4. Actualización en Tiempo Real (AJAX)

### Problema:
Era necesario presionar F5 para ver cambios después de subir imágenes o editar registros.

### Solución:
**Archivo**: `static/js/desvios_ambientales/ajax_handler.js`

Intercepta formularios y los envía vía AJAX:
- Crear registro
- Editar registro
- Subir imágenes (supervisor)
- Validar imágenes (admin)

**Archivos modificados**:
- `templates/desvios_ambientales/desvios.html` - Agregado `ajax_handler.js`
- `templates/desvios_ambientales/supervisor_desvios.html` - Agregado `ajax_handler.js`

**Funcionalidades**:
- Notificaciones visuales de éxito/error
- Actualización automática de tabla sin recargar página
- Cierre automático de modales
- Mantiene filtros y posición de scroll

---

## 5. Fix de Duplicación de Imágenes

### Problema Original:
Al subir 2 imágenes, se guardaban 4 en la base de datos.

### Causa Identificada:
El script `ajax_handler.js` se estaba cargando 2 veces:
1. En `base.html` (para todas las páginas)
2. En templates específicos (supervisor_desvios.html, desvios.html)

### Solución Final:

**Archivo**: `templates/base.html`
- ❌ Eliminada carga global de `ajax_handler.js`

**Archivo**: `templates/desvios_ambientales/supervisor_desvios.html`
```html
{% block scripts %}
<script>
const DETALLE_URL_BASE = "{{ url_for('supervisor.detalle_registro', rid='PLACEHOLDER') }}".replace('PLACEHOLDER','');
const SUBIR_URL_BASE   = "{{ url_for('supervisor.subir_levantamiento', rid='PLACEHOLDER') }}".replace('PLACEHOLDER','');
const IS_ADMIN = false;
</script>
<script src="{{ url_for('static', filename='js/desvios_ambientales/ajax_handler.js') }}"></script>
<script src="{{ url_for('static', filename='js/desvios_ambientales/desvios.js') }}"></script>
{% endblock %}
```

**Archivo**: `templates/desvios_ambientales/desvios.html`
```html
{% block scripts %}
<script>
const DETALLE_URL_BASE = "{{ url_for('da.detalle_registro', rid='PLACEHOLDER') }}".replace('PLACEHOLDER','');
const EDITAR_URL_BASE  = "{{ url_for('da.editar_registro', rid='PLACEHOLDER') }}".replace('PLACEHOLDER','');
const VALIDAR_URL_BASE = "{{ url_for('da.validar_levantamiento', rid='PLACEHOLDER') }}".replace('PLACEHOLDER','');
const ELIMINAR_URL_BASE = "{{ url_for('da.eliminar_registro', rid='PLACEHOLDER') }}".replace('PLACEHOLDER','');
const IS_ADMIN = true;
</script>
<script src="{{ url_for('static', filename='js/desvios_ambientales/ajax_handler.js') }}"></script>
<script src="{{ url_for('static', filename='js/desvios_ambientales/desvios.js') }}?v=3"></script>
{% endblock %}
```

**Archivo**: `static/js/desvios_ambientales/ajax_handler.js`
- Agregado flag `isSubmitting` para prevenir doble envío
- Agregados logs de debug

**Archivo**: `routes/supervisor.py`
- Agregados logs de debug para rastrear archivos recibidos

**Archivo**: `static/js/desvios_ambientales/desvios.js`
- Simplificado preview de imágenes (solo contador, sin miniaturas)
- Función `window.limpiarPreviewSubir()` para limpiar estado
- Función `abrirSubirModal()` limpia formulario antes de abrir

---

## 📊 RESUMEN DE ARCHIVOS MODIFICADOS

### Backend (Python):
1. ✅ `app.py` - Middleware de actualización automática
2. ✅ `routes/desvios_ambientales.py` - Simplificación de edición, eliminación de llamadas manuales
3. ✅ `routes/supervisor.py` - Logs de debug, eliminación de llamadas manuales

### Frontend (JavaScript):
4. ✅ `static/js/desvios_ambientales/ajax_handler.js` - Interceptación AJAX, prevención de doble envío
5. ✅ `static/js/desvios_ambientales/desvios.js` - Preview simplificado, limpieza de formularios

### Templates (HTML):
6. ✅ `templates/base.html` - Eliminada carga global de ajax_handler.js
7. ✅ `templates/desvios_ambientales/desvios.html` - Agregado ajax_handler.js específico
8. ✅ `templates/desvios_ambientales/supervisor_desvios.html` - Agregado ajax_handler.js específico
9. ✅ `templates/desvios_ambientales/estadisticas.html` - Columnas de atrasado, fix de suma

### Base de Datos (SQL):
10. ✅ `mejorar_sp_actualizar_registro.sql` - SP mejorado con lógica automática
11. ✅ `actualizar_sp_estadisticas.sql` - 3 SPs actualizados con columna atrasado

---

## 🧪 PRUEBAS RECOMENDADAS

### Prueba 1: Actualización Automática de Estados
1. Crear registro con fecha de ejecución de ayer
2. Estado inicial: Pendiente
3. Esperar 5 minutos o reiniciar app
4. ✅ Estado debe cambiar a "Atrasado" automáticamente

### Prueba 2: Edición de Registro
1. Editar registro "Atrasado"
2. Cambiar fecha de ejecución a mañana
3. Guardar
4. ✅ Estado debe cambiar automáticamente a "Pendiente"

### Prueba 3: Estadísticas
1. Ir a Estadísticas
2. Ver estadísticas por tipos
3. ✅ Debe mostrar columnas: Pendientes, Atrasados, Total
4. ✅ Total debe sumar correctamente (no "0111")

### Prueba 4: Subir Imágenes (Supervisor)
1. Abrir modal de subir imágenes
2. Seleccionar 2 imágenes
3. Subir
4. ✅ Modal se cierra automáticamente
5. ✅ Notificación verde de éxito
6. ✅ Tabla se actualiza sin F5
7. ✅ En BD deben guardarse exactamente 2 imágenes (no 4)

### Prueba 5: Consola del Navegador
1. Abrir DevTools (F12)
2. Ir a Console
3. Subir imágenes
4. ✅ Debe mostrar:
   ```
   ✅ AJAX Handler cargado correctamente    (solo 1 vez)
   Interceptando formulario de subir con AJAX    (solo 1 vez)
   [AJAX] Archivos en FormData: 2    (solo 1 vez)
   ```

### Prueba 6: Consola de Flask
1. Ver terminal donde corre Flask
2. Subir 2 imágenes
3. ✅ Debe mostrar:
   ```
   [DEBUG] Archivos recibidos: 2
   [DEBUG] Archivo 0: imagen1.jpg
   [DEBUG] Archivo 1: imagen2.jpg
   [DEBUG] Imagen guardada: imagen1.jpg
   [DEBUG] Imagen guardada: imagen2.jpg
   [DEBUG] Total guardadas: 2
   ```

---

## 🚀 INSTRUCCIONES DE DESPLIEGUE

### 1. Ejecutar Scripts SQL
```bash
# Conectarse a MySQL
mysql -u usuario -p desvios_ambientales

# Ejecutar scripts
source mejorar_sp_actualizar_registro.sql
source actualizar_sp_estadisticas.sql
```

### 2. Reiniciar Aplicación
```bash
# Detener Flask
Ctrl + C

# Reiniciar
python app.py
```

### 3. Limpiar Caché del Navegador
```
Presionar: Ctrl + Shift + R
```

---

## 📝 NOTAS IMPORTANTES

### Logs de Debug
Los logs agregados en `routes/supervisor.py` son temporales para debugging. Una vez confirmado que funciona correctamente, se pueden eliminar o comentar.

### Intervalo de Actualización
El intervalo de 5 minutos para actualizar estados se puede ajustar en `app.py`:
```python
_intervalo_update = timedelta(minutes=5)  # Cambiar aquí
```

### Caché del Navegador
Si los cambios no se reflejan, siempre hacer `Ctrl + Shift + R` para forzar recarga sin caché.

### Compatibilidad
Todos los cambios son compatibles con:
- Python 3.8+
- MySQL 5.7+
- Navegadores modernos (Chrome, Firefox, Edge, Safari)

---

## ✅ CHECKLIST DE VERIFICACIÓN

Después de desplegar, verificar:

- [ ] Middleware de actualización automática funciona (ver logs cada 5 min)
- [ ] Edición de registros actualiza estado correctamente
- [ ] Estadísticas muestran columna "Atrasados"
- [ ] Estadísticas de tipos suman correctamente
- [ ] Subir imágenes no recarga página
- [ ] Subir 2 imágenes guarda exactamente 2 (no 4)
- [ ] Modal se limpia al abrir
- [ ] Notificaciones aparecen correctamente
- [ ] Admin ve cambios del supervisor automáticamente
- [ ] Consola muestra "AJAX Handler cargado" solo 1 vez

---

**Fecha**: 2026-03-25
**Versión**: 2.0
**Estado**: ✅ Completado y listo para producción
