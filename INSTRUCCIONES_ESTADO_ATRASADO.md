# 🚀 Instrucciones de Implementación - Estado "Atrasado"

## 📋 Resumen
El estado "Atrasado" marca automáticamente los registros pendientes cuya fecha de ejecución ya pasó. El estado se guarda en la base de datos para mejor rendimiento y consistencia.

## ⚡ Instalación Rápida

### Paso 1: Ejecutar Migración
```bash
cd ecosupervisor
mysql -u tu_usuario -p desvios_ambientales < migration_add_atrasado.sql
```

Esto hará:
- ✅ Agregar el estado "Atrasado" a la tabla `Tbl_Estado`
- ✅ Crear el stored procedure `SP_ActualizarEstadosAtrasados`
- ✅ Actualizar `SP_DashboardStats`
- ✅ Marcar registros existentes como "Atrasado" si corresponde

### Paso 2: Verificar
```sql
-- Ver estados
SELECT * FROM Tbl_Estado ORDER BY Orden;

-- Ver registros atrasados
SELECT r.Codigo, r.FechaEjecucion, e.Estado 
FROM Tbl_Registro r
JOIN Tbl_Estado e ON e.idEstado = r.idEstado
WHERE e.Estado = 'Atrasado';
```

### Paso 3: Probar
1. Accede al dashboard o lista de desvíos
2. Los registros con fecha de ejecución vencida deben aparecer en rojo como "ATRASADO"
3. Puedes filtrar por estado "Atrasado"

## 🔄 Funcionamiento

### Actualización Automática
El estado se actualiza automáticamente cuando:
- Un usuario accede al dashboard
- Un usuario accede a la lista de desvíos (admin o supervisor)
- Se ejecuta el cron job (opcional)

### Lógica
```
SI registro.estado == "Pendiente" 
   Y registro.fecha_ejecucion < fecha_actual
ENTONCES
   registro.estado = "Atrasado"
```

### Reversión Automática
Si editas un registro "Atrasado" y cambias la fecha de ejecución a futuro, el sistema lo marca automáticamente como "Pendiente".

## 🤖 Automatización (Opcional)

Para mantener los estados actualizados sin depender de visitas de usuarios:

### Configurar Cron Job
```bash
# Editar crontab
crontab -e

# Agregar línea (ejecutar cada hora)
0 * * * * cd /ruta/completa/a/ecosupervisor && python actualizar_estados_atrasados.py >> logs/estados_atrasados.log 2>&1
```

### Crear Directorio de Logs
```bash
mkdir -p logs
```

### Ejecutar Manualmente
```bash
python actualizar_estados_atrasados.py
```

Salida esperada:
```
============================================================
Actualizando estados atrasados...
============================================================
[2024-03-25 10:30:00] ✓ Actualización completada: 5 registros marcados como 'Atrasado'
```

## 📊 Visualización

### Badge Rojo
Los registros atrasados se muestran con un badge rojo:
- Fondo: Rojo pastel
- Texto: Rojo oscuro
- Peso: Bold

### Filtros
El estado "Atrasado" aparece en:
- Filtro de estados (dropdown)
- Estadísticas del dashboard (incluido en "pendientes")
- Exportaciones Excel

## 👥 Permisos por Rol

| Acción | Administrador | Supervisor | Trabajador |
|--------|---------------|------------|------------|
| Ver registros atrasados | ✅ | ✅ | ✅ |
| Subir imágenes | ✅ | ✅ | ✅ |
| Editar registro | ✅ | ❌ | ❌ |
| Cambiar estado manualmente | ✅ | ❌ | ❌ |

## 🔍 Consultas SQL Útiles

### Ver todos los atrasados
```sql
SELECT r.Codigo, r.Descripcion, r.FechaEjecucion, 
       ar.AreaResponsable, r.PersonalResponsable
FROM Tbl_Registro r
JOIN Tbl_Estado e ON e.idEstado = r.idEstado
JOIN Tbl_AreaResponsable ar ON ar.idAreaResponsable = r.idAreaResponsable
WHERE e.Estado = 'Atrasado'
ORDER BY r.FechaEjecucion;
```

### Contar atrasados por área
```sql
SELECT ar.AreaResponsable, COUNT(*) as total_atrasados
FROM Tbl_Registro r
JOIN Tbl_Estado e ON e.idEstado = r.idEstado
JOIN Tbl_AreaResponsable ar ON ar.idAreaResponsable = r.idAreaResponsable
WHERE e.Estado = 'Atrasado'
GROUP BY ar.idAreaResponsable, ar.AreaResponsable
ORDER BY total_atrasados DESC;
```

### Actualizar manualmente
```sql
CALL SP_ActualizarEstadosAtrasados();
```

## 🐛 Solución de Problemas

### El estado no se actualiza
1. Verificar que el stored procedure existe:
   ```sql
   SHOW PROCEDURE STATUS WHERE Name = 'SP_ActualizarEstadosAtrasados';
   ```

2. Ejecutar manualmente:
   ```sql
   CALL SP_ActualizarEstadosAtrasados();
   ```

3. Verificar permisos de la BD

### Los registros no aparecen en rojo
1. Limpiar caché del navegador (Ctrl + F5)
2. Verificar que el CSS tiene la clase `.estado-atrasado`
3. Inspeccionar el elemento en el navegador

### El cron job no funciona
1. Verificar que el path es absoluto
2. Verificar permisos de ejecución:
   ```bash
   chmod +x actualizar_estados_atrasados.py
   ```
3. Revisar logs:
   ```bash
   tail -f logs/estados_atrasados.log
   ```

## 📚 Archivos Relacionados

- `migration_add_atrasado.sql` - Script de migración
- `actualizar_estados_atrasados.py` - Script para cron job
- `ESTADO_ATRASADO.md` - Documentación técnica completa
- `CAMBIOS_ESTADO_ATRASADO.md` - Resumen de cambios

## ✅ Checklist de Implementación

- [ ] Ejecutar `migration_add_atrasado.sql`
- [ ] Verificar que el estado "Atrasado" existe en la BD
- [ ] Probar accediendo al dashboard
- [ ] Verificar que los registros atrasados aparecen en rojo
- [ ] Probar el filtro por estado "Atrasado"
- [ ] (Opcional) Configurar cron job
- [ ] (Opcional) Probar el script `actualizar_estados_atrasados.py`

## 🎉 ¡Listo!

El estado "Atrasado" está completamente implementado y funcionando. Los registros se actualizarán automáticamente cada vez que alguien acceda al sistema.
