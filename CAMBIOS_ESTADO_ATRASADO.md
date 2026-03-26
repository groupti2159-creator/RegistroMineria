# Resumen de Cambios - Estado "Atrasado"

## ⚠️ IMPORTANTE: Estado Persistente en Base de Datos

El estado "Atrasado" **SE GUARDA EN LA BASE DE DATOS** mediante un stored procedure que se ejecuta automáticamente.

## Archivos Modificados

### 1. `routes/desvios_ambientales.py`
**Cambios:**
- Agregada llamada a `SP_ActualizarEstadosAtrasados` en `dashboard()`
- Agregada llamada a `SP_ActualizarEstadosAtrasados` en `registrar()`
- Agregada lógica en `editar_registro()` para ajustar estado según fecha de ejecución
- Actualizado el orden de estados

### 2. `routes/supervisor.py`
**Cambios:**
- Agregada llamada a `SP_ActualizarEstadosAtrasados` en `desvios()`
- Actualizado el orden de estados

### 3. `templates/desvios_ambientales/supervisor_desvios.html`
**Cambios:**
- Actualizado el banner informativo para mencionar "PENDIENTES o ATRASADOS"

### 4. `static/css/main.css`
**Cambios:**
- Agregados hover effects para `.estado-atrasado` en modo claro y oscuro

### 5. `schema.sql`
**Cambios:**
- Agregado estado "Atrasado" en la tabla `Tbl_Estado`
- Creado stored procedure `SP_ActualizarEstadosAtrasados`
- Actualizado `SP_DashboardStats` para incluir "Atrasado" en pendientes

## Archivos Nuevos Creados

### 1. `migration_add_atrasado.sql`
Script de migración completo que:
- Agrega el estado "Atrasado" si no existe
- Crea el stored procedure `SP_ActualizarEstadosAtrasados`
- Actualiza `SP_DashboardStats`
- Ejecuta el procedimiento para actualizar registros existentes

### 2. `actualizar_estados_atrasados.py`
Script Python para ejecutar como cron job (opcional):
- Actualiza estados atrasados sin necesidad de visitas de usuarios
- Puede ejecutarse cada hora automáticamente
- Genera logs de las actualizaciones

### 3. `ESTADO_ATRASADO.md`
Documentación completa sobre el funcionamiento.

### 4. `CAMBIOS_ESTADO_ATRASADO.md` (este archivo)
Resumen de todos los cambios realizados.

## Stored Procedure Creado

### `SP_ActualizarEstadosAtrasados`
```sql
CREATE PROCEDURE SP_ActualizarEstadosAtrasados()
BEGIN
    DECLARE v_id_atrasado INT;
    SELECT idEstado INTO v_id_atrasado FROM Tbl_Estado WHERE Estado = 'Atrasado' LIMIT 1;
    
    UPDATE Tbl_Registro r
    JOIN Tbl_Estado e ON e.idEstado = r.idEstado
    SET r.idEstado = v_id_atrasado
    WHERE e.Estado = 'Pendiente'
      AND r.FechaEjecucion IS NOT NULL
      AND DATE(r.FechaEjecucion) < CURDATE()
      AND r.Archivado = 0;
    
    SELECT ROW_COUNT() AS registros_actualizados;
END
```

## Cómo Migrar

### 1. Ejecutar Script de Migración
```bash
mysql -u usuario -p desvios_ambientales < ecosupervisor/migration_add_atrasado.sql
```

### 2. (Opcional) Configurar Cron Job
Para actualizar estados automáticamente cada hora:
```bash
crontab -e
# Agregar:
0 * * * * cd /ruta/a/ecosupervisor && python actualizar_estados_atrasados.py >> logs/estados_atrasados.log 2>&1
```

### 3. Verificar
```sql
-- Ver estados
SELECT * FROM Tbl_Estado ORDER BY Orden;

-- Ver registros atrasados
SELECT r.Codigo, r.FechaEjecucion, e.Estado 
FROM Tbl_Registro r
JOIN Tbl_Estado e ON e.idEstado = r.idEstado
WHERE e.Estado = 'Atrasado';
```

## Roles que Pueden Ver "Atrasado"

✅ **Administrador**: Puede ver y gestionar registros atrasados
✅ **Supervisor**: Puede ver registros atrasados y subir imágenes de levantamiento
✅ **Trabajador**: Puede ver registros atrasados (usa la misma vista que supervisor)

## Comportamiento Esperado

✅ Los registros con estado "Pendiente" y `FechaEjecucion < fecha_actual` se actualizan a "Atrasado" en la BD
✅ El badge es de color rojo para indicar urgencia
✅ Aparece en el filtro de estados (tanto admin como supervisor)
✅ Se puede filtrar por "Atrasado"
✅ Funciona en modo claro y oscuro
✅ Los supervisores pueden subir imágenes en registros "Atrasados"
✅ Al editar la fecha de ejecución a futuro, el registro vuelve a "Pendiente"
✅ Se puede consultar directamente en SQL por estado "Atrasado"
✅ Las estadísticas incluyen "Atrasado" correctamente

## Ventajas de Esta Implementación

✅ **Persistencia**: El estado se guarda en la base de datos
✅ **Consultas SQL**: Se puede filtrar y consultar directamente
✅ **Estadísticas**: Los reportes muestran datos correctos
✅ **Rendimiento**: No se calcula en cada carga de página
✅ **Consistencia**: Todos los usuarios ven el mismo estado
✅ **Automatización**: Puede ejecutarse como cron job
✅ **Reversible**: Si se actualiza la fecha, vuelve a "Pendiente"

## Flujo de Actualización

1. Usuario accede a dashboard o lista de desvíos
2. Se ejecuta `SP_ActualizarEstadosAtrasados`
3. La BD actualiza registros Pendientes con fecha vencida
4. Se cargan los registros con estados actualizados
5. Los registros "Atrasados" se muestran en rojo

**Alternativa con Cron Job:**
1. Cron ejecuta `actualizar_estados_atrasados.py` cada hora
2. El script llama a `SP_ActualizarEstadosAtrasados`
3. Los estados se mantienen actualizados sin visitas de usuarios
