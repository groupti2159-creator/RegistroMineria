# Estado "Atrasado" - Documentación

## Descripción
El estado "Atrasado" se activa automáticamente cuando un registro con estado "Pendiente" tiene una fecha de ejecución (`FechaEjecucion`) que ya pasó.

## Funcionamiento

### Actualización Automática en Base de Datos
- El estado "Atrasado" **SE GUARDA EN LA BASE DE DATOS**
- Se actualiza automáticamente mediante el stored procedure `SP_ActualizarEstadosAtrasados`
- Este procedimiento se ejecuta cada vez que se cargan los registros (dashboard, lista de desvíos)
- También puede ejecutarse como cron job para mantener los estados actualizados

### Lógica del Stored Procedure
```sql
-- Actualiza registros Pendientes con fecha de ejecución vencida a Atrasado
UPDATE Tbl_Registro r
JOIN Tbl_Estado e ON e.idEstado = r.idEstado
SET r.idEstado = (SELECT idEstado FROM Tbl_Estado WHERE Estado = 'Atrasado')
WHERE e.Estado = 'Pendiente'
  AND r.FechaEjecucion IS NOT NULL
  AND DATE(r.FechaEjecucion) < CURDATE()
  AND r.Archivado = 0;
```

### Actualización al Editar
- Si se edita un registro "Atrasado" y se cambia la fecha de ejecución a futuro, vuelve a "Pendiente"
- Si se edita un registro "Pendiente" y la fecha de ejecución es pasada, se marca como "Atrasado"

### Visualización
- El badge del estado "Atrasado" se muestra en **color rojo** (fondo rojo pastel con texto rojo oscuro)
- Aparece en la tabla de registros con el mismo formato que otros estados
- Se puede filtrar por estado "Atrasado" en el selector de filtros

### Orden de Estados
1. Pendiente
2. **Atrasado** ← Estado persistente en BD
3. Asignado
4. En Proceso
5. Enviado
6. En Revisión
7. Culminado
8. Rechazado
9. Cerrado

## Implementación Técnica

### Backend (Python)
- Archivo: `routes/desvios_ambientales.py`
- Funciones afectadas:
  - `dashboard()`: Llama a `SP_ActualizarEstadosAtrasados` antes de cargar datos
  - `registrar()`: Llama a `SP_ActualizarEstadosAtrasados` antes de cargar datos
  - `editar_registro()`: Valida y ajusta el estado según la fecha de ejecución

- Archivo: `routes/supervisor.py`
- Funciones afectadas:
  - `desvios()`: Llama a `SP_ActualizarEstadosAtrasados` antes de cargar datos

### Base de Datos
- Tabla: `Tbl_Estado`
- Registro: `('Atrasado', 'Registro pendiente con fecha de ejecución vencida', 2)`
- Stored Procedure: `SP_ActualizarEstadosAtrasados`
- Migración: Ejecutar `migration_add_atrasado.sql`

### Frontend (CSS)
- Archivo: `static/css/main.css`
- Clase: `.estado-atrasado`
- Estilo: Fondo rojo pastel (`var(--pastel-red)`) con texto rojo (`var(--text-red)`)

## Automatización (Opcional)

### Cron Job
Para mantener los estados actualizados automáticamente sin depender de las visitas de usuarios:

```bash
# Editar crontab
crontab -e

# Agregar línea para ejecutar cada hora
0 * * * * cd /ruta/a/ecosupervisor && python actualizar_estados_atrasados.py >> logs/estados_atrasados.log 2>&1
```

### Script Python
El archivo `actualizar_estados_atrasados.py` puede ejecutarse manualmente:
```bash
python actualizar_estados_atrasados.py
```

## Migración
Si tu base de datos ya está en producción, ejecuta:
```bash
mysql -u usuario -p desvios_ambientales < migration_add_atrasado.sql
```

Este script:
1. Agrega el estado "Atrasado" si no existe
2. Crea el stored procedure `SP_ActualizarEstadosAtrasados`
3. Actualiza el `SP_DashboardStats` para incluir "Atrasado" en pendientes
4. Ejecuta el procedimiento para actualizar registros existentes

## Comportamiento del Usuario
- Los registros "Atrasados" funcionan igual que los "Pendientes"
- Los supervisores pueden subir imágenes de levantamiento
- Se pueden editar y gestionar normalmente
- La única diferencia es la visualización en rojo para indicar urgencia
- Al editar la fecha de ejecución a futuro, el registro vuelve a "Pendiente"

## Ventajas de Guardar en BD

✅ Se pueden hacer consultas SQL directamente por estado "Atrasado"
✅ Las estadísticas incluyen "Atrasado" como estado real
✅ Los reportes y exportaciones muestran el estado correcto
✅ Mejor rendimiento (no se calcula en cada carga)
✅ Consistencia de datos entre diferentes vistas
