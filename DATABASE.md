# Documentación de Base de Datos

## Información General
- **Motor**: MySQL 8.0
- **Charset**: utf8mb4
- **Collation**: utf8mb4_unicode_ci
- **Zona Horaria**: America/Lima (UTC-5)

## Tablas Principales

### tbl_roles
Roles del sistema
- `idroles` (VARCHAR(20), PK)
- `nombrerol` (VARCHAR(50))

**Datos**:
- `ROL001`: Administrador
- `ROL002`: Supervisor
- `ROL003`: Trabajador

### tbl_usuario
Usuarios del sistema
- `idusuario` (VARCHAR(20), PK)
- `dni` (VARCHAR(8), UNIQUE)
- `nombrecompleto` (VARCHAR(100))
- `password` (VARCHAR(255))
- `activo` (TINYINT, default 1)

### tbl_usuariorol
Relación usuario-rol
- `idusuariorol` (VARCHAR(20), PK)
- `idusuario` (VARCHAR(20), FK)
- `idroles` (VARCHAR(20), FK)

### tbl_estado
Estados de reportes
- `idestado` (VARCHAR(20), PK)
- `estado` (VARCHAR(50))
- `orden` (INT)

**Estados principales**:
- `EST001`: Pendiente
- `EST003`: En Proceso
- `EST006`: Culminado

### tbl_areareportante
Áreas que reportan desvíos
- `idareareportante` (VARCHAR(20), PK)
- `areareportante` (VARCHAR(100))

### tbl_arearesponsable
Áreas responsables de solucionar
- `idarearesponsable` (VARCHAR(20), PK)
- `arearesponsable` (VARCHAR(100))

### tbl_ubicacion
Ubicaciones de la mina
- `idubicacion` (VARCHAR(20), PK)
- `ubicacion` (VARCHAR(200))

### tbl_riesgo
Niveles de riesgo
- `idriesgo` (VARCHAR(20), PK)
- `riesgo` (VARCHAR(50))

**Niveles**:
- `RIE001`: Bajo
- `RIE002`: Medio
- `RIE003`: Alto

### tbl_descripciontipo
Tipos de desvíos
- `iddescripciontipo` (VARCHAR(20), PK)
- `descripciontipo` (VARCHAR(100))

### tbl_registro
Registro principal de desvíos
- `idregistro` (VARCHAR(20), PK)
- `codigo` (VARCHAR(20), UNIQUE) - Correlativo
- `fechainicio` (DATE)
- `fechaejecucion` (DATE)
- `descripcion` (TEXT)
- `accion` (TEXT)
- `notaslevantamiento` (TEXT)
- `personalresponsable` (VARCHAR(100))
- `cctaresponsable` (VARCHAR(50))
- `idestado` (VARCHAR(20), FK)
- `idareareportante` (VARCHAR(20), FK)
- `idarearesponsable` (VARCHAR(20), FK)
- `idubicacion` (VARCHAR(20), FK)
- `idriesgo` (VARCHAR(20), FK)
- `iddescripciontipo` (VARCHAR(20), FK)
- `idusuariorol` (VARCHAR(20), FK) - Creador
- `fechacreacion` (DATETIME)
- `archivado` (TINYINT, default 0)
- `fechaarchivado` (DATETIME)
- `idusuariorolarchivador` (VARCHAR(20), FK)

### tbl_tipoimagen
Tipos de imágenes
- `idtipoimagen` (VARCHAR(20), PK)
- `tipoimagen` (VARCHAR(50))

**Tipos**:
- `TIM001`: ImagenError (Evidencia)
- `TIM002`: ImagenLevantamiento

### tbl_estadoimagen
Estados de imágenes
- `idestadoimagen` (VARCHAR(20), PK)
- `estadoimagen` (VARCHAR(50))

**Estados**:
- `EIM001`: Pendiente
- `EIM002`: Aprobada
- `EIM003`: Rechazada

### tbl_imagenregistro
Imágenes asociadas a registros
- `idimagen` (VARCHAR(20), PK)
- `idregistro` (VARCHAR(20), FK)
- `idusuariorol` (VARCHAR(20), FK) - Quien subió
- `idtipoimagen` (VARCHAR(20), FK)
- `idestadoimagen` (VARCHAR(20), FK)
- `rutaimagen` (VARCHAR(255))
- `nombrearchivo` (VARCHAR(255))
- `tamanokb` (INT)
- `fechasubida` (DATETIME)

### tbl_validacionimagen
Validaciones de imágenes
- `idvalidacion` (VARCHAR(20), PK)
- `idimagen` (VARCHAR(20), FK)
- `idregistro` (VARCHAR(20), FK)
- `idusuariorol` (VARCHAR(20), FK) - Validador
- `decision` (ENUM: 'APROBADA', 'RECHAZADA')
- `motivorechazo` (TEXT)
- `fecharevision` (DATETIME)

### tbl_notificacion
Notificaciones del sistema
- `idnotificacion` (VARCHAR(20), PK)
- `idusuariorol` (VARCHAR(20), FK)
- `mensaje` (TEXT)
- `tipo` (VARCHAR(20)) - info, success, warning, error
- `leida` (TINYINT, default 0)
- `fechacreacion` (DATETIME)
- `idregistro` (VARCHAR(20), FK) - Opcional

## Stored Procedures

### Autenticación
- `sp_login(dni, password)` - Login de usuario

### Dashboard
- `sp_dashboardstats()` - Estadísticas para dashboard

### Registros
- `sp_siguientecorrelativo()` - Obtener siguiente código correlativo
- `sp_crearregistro(...)` - Crear nuevo registro
- `sp_actualizarregistro(...)` - Actualizar registro existente
- `sp_listarregistros(estado_filter)` - Listar registros (admin)
- `sp_listarregistrossupervisor(estado_filter)` - Listar registros (supervisor)
- `sp_detalleregistro(idregistro)` - Detalle de un registro
- `sp_archivarregistro(idregistro, idusuariorol)` - Archivar registro

### Imágenes
- `sp_guardarimagen(...)` - Guardar nueva imagen
- `sp_imagenesregistro(idregistro)` - Obtener imágenes de un registro
- `sp_validarimagen(...)` - Validar imagen (aprobar/rechazar)
- `sp_eliminarimagen(idimagen)` - Eliminar imagen físicamente

### Notificaciones
- `sp_crearnotificacion(...)` - Crear notificación
- `sp_notificaciones(idusuariorol)` - Obtener notificaciones de usuario
- `sp_contarnotificaciones(idusuariorol)` - Contar notificaciones no leídas
- `sp_leernotificacion(idnotificacion)` - Marcar notificación como leída

### Historial
- `sp_historialadmin()` - Historial completo (admin)
- `sp_historialsupervisor(idusuariorol)` - Historial personal (supervisor)

### Exportación
- `sp_exportarregistros()` - Obtener datos para exportar a Excel

## Vistas

### vw_registros_completos
Vista con información completa de registros incluyendo:
- Datos del registro
- Estado
- Áreas (reportante y responsable)
- Ubicación
- Riesgo
- Tipo de desvío
- Creador
- Contadores de imágenes

## Triggers

### trg_actualizar_estado_registro
- **Tabla**: tbl_imagenregistro
- **Evento**: AFTER INSERT
- **Acción**: Cambia estado del registro a "En Proceso" cuando se suben levantamientos

### trg_actualizar_estado_validacion
- **Tabla**: tbl_validacionimagen
- **Evento**: AFTER INSERT
- **Acción**: 
  - Si APROBADA: Cambia estado del registro a "Culminado"
  - Si RECHAZADA: Cambia estado del registro a "Pendiente"

## Índices

Todas las tablas tienen índices en:
- Claves primarias (PK)
- Claves foráneas (FK)
- Campos de búsqueda frecuente (dni, codigo, fechacreacion)

## Consideraciones Importantes

### Case Sensitivity
- **Linux/Railway**: MySQL es case-sensitive
- **Windows**: MySQL es case-insensitive por defecto
- **Solución**: Todas las tablas, columnas y referencias en minúsculas

### Zona Horaria
- Configurada en UTC-5 (Perú)
- Fechas almacenadas en DATETIME
- Conversión automática en stored procedures

### Integridad Referencial
- Todas las relaciones tienen ON DELETE CASCADE o ON DELETE SET NULL
- Validaciones en stored procedures

### Seguridad
- Contraseñas hasheadas (aunque en demo están en texto plano)
- Validación de permisos en stored procedures
- Sanitización de inputs

## Backup y Restauración

### Backup
```bash
mysqldump -u root -p desvios_ambientales > backup.sql
```

### Restauración
```bash
mysql -u root -p desvios_ambientales < backup.sql
```

### Backup Solo Estructura
```bash
mysqldump -u root -p --no-data desvios_ambientales > schema_only.sql
```

### Backup Solo Datos
```bash
mysqldump -u root -p --no-create-info desvios_ambientales > data_only.sql
```

## Mantenimiento

### Optimizar Tablas
```sql
OPTIMIZE TABLE tbl_registro;
OPTIMIZE TABLE tbl_imagenregistro;
```

### Analizar Tablas
```sql
ANALYZE TABLE tbl_registro;
```

### Verificar Integridad
```sql
CHECK TABLE tbl_registro;
```

### Reparar Tablas (si es necesario)
```sql
REPAIR TABLE tbl_registro;
```
