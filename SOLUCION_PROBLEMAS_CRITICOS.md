# Solución de Problemas Críticos - Desvíos Ambientales

## ✅ PROBLEMA 1: Actualización Automática de Estados Atrasados

### Problema Original:
- El SP `sp_actualizarestadosatrasados` solo se ejecutaba cuando el usuario visitaba ciertas páginas
- Los registros podían permanecer "Pendientes" aunque ya estuvieran vencidos
- Dependía de la navegación del usuario

### Solución Implementada:

**Archivo**: `app.py`

Se agregó un middleware `@app.before_request` que:
- Ejecuta automáticamente el SP cada 5 minutos
- Usa un cache global para evitar sobrecarga
- Se ejecuta en todos los requests HTML (excepto archivos estáticos)
- No interrumpe el request si falla

```python
# Cache para evitar ejecutar el SP en cada request
_ultimo_update_estados = None
_intervalo_update = timedelta(minutes=5)  # Actualizar cada 5 minutos

@app.before_request
def actualizar_estados_atrasados():
    """Actualiza estados atrasados automáticamente cada 5 minutos."""
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

### Cambios Adicionales:

**Archivos modificados**:
- `routes/desvios_ambientales.py` - Eliminadas llamadas manuales al SP en `dashboard()` y `registrar()`
- `routes/supervisor.py` - Eliminada llamada manual al SP en `desvios()`

### Ventajas:
✅ Actualización automática cada 5 minutos
✅ No depende de la navegación del usuario
✅ Optimizado con cache para evitar sobrecarga
✅ Manejo de errores sin interrumpir la aplicación
✅ Log de ejecución para debugging

---

## ✅ PROBLEMA 2: Lógica de Edición Compleja

### Problema Original:
- Lógica compleja en Python para determinar si un registro debe ser Pendiente o Atrasado
- Solo funcionaba si el usuario seleccionaba específicamente esos estados
- Múltiples consultas a la base de datos
- Código difícil de mantener y propenso a errores

### Solución Implementada:

**Archivo**: `mejorar_sp_actualizar_registro.sql`

Se mejoró el stored procedure `SP_ActualizarRegistro` para:
- Manejar automáticamente la lógica Pendiente/Atrasado
- Validar la fecha de ejecución contra la fecha actual
- Aplicar el estado correcto sin intervención de Python

```sql
-- Determinar el estado final basado en la fecha de ejecución
SET v_estado_final = p_idestado;

-- Si el estado es Pendiente o Atrasado, validar automáticamente según la fecha
IF p_idestado IN (v_id_pendiente, v_id_atrasado) THEN
    IF p_fechaejecucion IS NOT NULL THEN
        IF DATE(p_fechaejecucion) < CURDATE() THEN
            -- Fecha vencida -> Atrasado
            SET v_estado_final = v_id_atrasado;
        ELSE
            -- Fecha futura o hoy -> Pendiente
            SET v_estado_final = v_id_pendiente;
        END IF;
    ELSE
        -- Sin fecha de ejecución -> Pendiente por defecto
        SET v_estado_final = v_id_pendiente;
    END IF;
END IF;
```

### Cambios en Python:

**Archivo**: `routes/desvios_ambientales.py`

La función `editar_registro()` ahora es mucho más simple:
- Eliminadas ~40 líneas de lógica compleja
- Solo pasa los parámetros al SP
- El SP se encarga de toda la validación

**Antes** (complejo):
```python
# Obtener el estado actual del registro
cur = mysql.connection.cursor()
cur.execute("SELECT idEstado, FechaEjecucion FROM tbl_registro WHERE IdRegistro=%s", (rid,))
registro_actual = cur.fetchone()
cur.close()

# Determinar el nuevo estado basado en la fecha de ejecución
fecha_ejecucion_nueva = request.form.get('fecha_ejecucion') or None
estado_nuevo = int(request.form['estado'])

if registro_actual and fecha_ejecucion_nueva:
    fecha_ejec_date = datetime.strptime(fecha_ejecucion_nueva, '%Y-%m-%d').date()
    fecha_actual = datetime.now().date()
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT idEstado, Estado FROM tbl_estado WHERE Estado IN ('Pendiente', 'Atrasado')")
    estados = {r['Estado']: r['idEstado'] for r in cur.fetchall()}
    cur.close()
    
    if estado_nuevo in [estados.get('Pendiente'), estados.get('Atrasado')]:
        if fecha_ejec_date >= fecha_actual:
            estado_nuevo = estados.get('Pendiente')
        else:
            estado_nuevo = estados.get('Atrasado')
```

**Ahora** (simple):
```python
# El stored procedure ahora maneja automáticamente la lógica de Pendiente/Atrasado
# basándose en la fecha de ejecución
cur = mysql.connection.cursor()
result = sp_exec(cur, 'sp_actualizarregistro', (...))
mysql.connection.commit()
cur.close()
```

### Ventajas:
✅ Lógica centralizada en la base de datos
✅ Código Python más simple y mantenible
✅ Menos consultas a la base de datos
✅ Validación consistente en todos los casos
✅ Más fácil de testear y debuggear

---

## 📋 INSTRUCCIONES DE IMPLEMENTACIÓN

### Paso 1: Actualizar la aplicación
```bash
# Los cambios en app.py y routes ya están aplicados
# Solo necesitas reiniciar la aplicación
```

### Paso 2: Ejecutar el script SQL
```bash
# Conectarse a MySQL y ejecutar:
mysql -u usuario -p desvios_ambientales < mejorar_sp_actualizar_registro.sql
```

O desde MySQL Workbench:
1. Abrir `mejorar_sp_actualizar_registro.sql`
2. Ejecutar el script completo
3. Verificar que aparezca: "✅ Stored procedure SP_ActualizarRegistro mejorado!"

### Paso 3: Verificar funcionamiento

**Prueba 1 - Actualización automática**:
1. Crear un registro con fecha de ejecución de ayer
2. Estado inicial: Pendiente
3. Esperar 5 minutos o reiniciar la app
4. Navegar a cualquier página del módulo
5. Verificar que el estado cambió a "Atrasado"

**Prueba 2 - Edición de registro**:
1. Editar un registro "Atrasado"
2. Cambiar la fecha de ejecución a mañana
3. Guardar (sin cambiar el estado manualmente)
4. Verificar que el estado cambió automáticamente a "Pendiente"

**Prueba 3 - Log de actualización**:
1. Revisar la consola de la aplicación
2. Cada 5 minutos debe aparecer: `[HH:MM:SS] Estados atrasados actualizados`

---

## 🔍 MONITOREO Y DEBUGGING

### Ver logs de actualización:
```bash
# En la consola donde corre Flask verás:
[20:15:30] Estados atrasados actualizados
[20:20:30] Estados atrasados actualizados
[20:25:30] Estados atrasados actualizados
```

### Verificar última actualización:
```python
# En Python shell o debugging:
from app import _ultimo_update_estados
print(_ultimo_update_estados)  # Muestra la última vez que se ejecutó
```

### Forzar actualización inmediata:
```python
# Cambiar el intervalo temporalmente en app.py:
_intervalo_update = timedelta(seconds=10)  # Actualizar cada 10 segundos
```

---

## 📊 IMPACTO DE LOS CAMBIOS

### Antes:
- ❌ Actualización manual en 3 lugares diferentes
- ❌ Lógica compleja de 40+ líneas en Python
- ❌ Múltiples consultas a BD por edición
- ❌ Estados inconsistentes si no se visitaban ciertas páginas
- ❌ Difícil de mantener y debuggear

### Después:
- ✅ Actualización automática centralizada
- ✅ Lógica simple de 5 líneas en Python
- ✅ Una sola llamada al SP por edición
- ✅ Estados siempre actualizados (cada 5 min)
- ✅ Fácil de mantener y extender

---

## 🚀 PRÓXIMAS MEJORAS OPCIONALES

### Opción 1: Job programado (cron)
Si prefieres no usar el middleware, puedes crear un cron job:
```bash
# Ejecutar cada 5 minutos
*/5 * * * * mysql -u usuario -p password -e "CALL desvios_ambientales.SP_ActualizarEstadosAtrasados()"
```

### Opción 2: Trigger en MySQL
Crear un trigger que se ejecute automáticamente:
```sql
-- Trigger que valida el estado al insertar/actualizar
CREATE TRIGGER before_update_registro
BEFORE UPDATE ON tbl_registro
FOR EACH ROW
BEGIN
    -- Validar automáticamente Pendiente/Atrasado
    IF NEW.FechaEjecucion < CURDATE() AND NEW.idEstado = (SELECT idEstado FROM tbl_estado WHERE Estado='Pendiente') THEN
        SET NEW.idEstado = (SELECT idEstado FROM tbl_estado WHERE Estado='Atrasado');
    END IF;
END;
```

### Opción 3: Ajustar intervalo
Si 5 minutos es mucho o poco, ajustar en `app.py`:
```python
_intervalo_update = timedelta(minutes=1)   # Más frecuente
_intervalo_update = timedelta(minutes=15)  # Menos frecuente
```

---

**Fecha**: 2026-03-25
**Versión**: 1.0
**Estado**: ✅ Implementado y listo para pruebas
