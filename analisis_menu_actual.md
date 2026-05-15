# Análisis de Estructura del Menú

## Datos de la Tabla tbl_modulo

| ID | Código | Nombre | Icono | URL | Orden | idmodulopadre |
|----|--------|--------|-------|-----|-------|---------------|
| 1 | DASHBOARD | Desvíos ambientales | home | - | 1 | 1 |
| 2 | DESVIOS | Registrar Reporte | alert-triangle | /admin/registrar | 1 | 2 |
| 3 | ESTADISTICAS | Estadísticas | bar-chart-2 | /admin/estadisticas | 1 | 3 |
| 4 | CONFIGURACION | Configuración | settings | - | 50 | - |
| 5 | MIS_REPORTES | Mis Reportes | clipboard | /supervisor/desvios | 1 | 1 |
| 16 | GESTION_RESIDUOS | Gestión de Residuos | trash-2 | - | 20 | - |
| 17 | GENERACION_DIARIA | Generación Diaria | calendar | /admin/residuos/generacion | 2 | 1 |
| 18 | COMERCIALIZABLE | Comercializable | package | /admin/residuos/comercializable | 2 | 2 |
| 19 | DISPOSICION_MATPEL | Disposición Matpel | alert-octagon | /admin/residuos/matpel | 2 | 3 |
| 20 | COMPOSTAJE | Compostaje | leaf | /admin/residuos/compostaje | 2 | 4 |
| 25 | DESVIOS_AMB | Desvíos ambientales | alert-triangle | - | 10 | - |
| 26 | COMPROMISOS_REG | Registro | check-square | /admin/compromisos | 3 | 1 |
| 27 | DATA_METRO_INFO | Información | cloud | /admin/meteorologia | 4 | 1 |
| 28 | CONFIG_USUARIOS | Configuración de Usuarios | users | /admin/configuracion/usuarios | 5 | 1 |
| 29 | COMPROMISOS_DASH | Dashboard | layout | /admin/compromisos/dashboard | 3 | 1 |
| 30 | COMPROMISOS | Registro | check-square | /admin/compromisos/registro | 3 | 2 |
| 31 | DATA_METRO_DASH | Dashboard | layout | /admin/meteorologia/dashboard | 4 | 1 |
| 32 | DATA_METEOROLOGICA | Información | cloud | /admin/meteorologia | 4 | 2 |
| 33 | GESTION_AGUAS | Gestión de Aguas | droplet | - | 60 | - |
| 34 | AGUAS_DASHBOARD | Dashboard | home | /admin/aguas/dashboard | 6 | 1 |
| 35 | MONITOREO_AMBIENTAL | Monitoreo Ambiental | activity | /admin/aguas | 6 | 2 |
| 36 | REPORTE_ANA | Reportes ANA | clipboard | /admin/ana | 6 | 3 |
| 45 | ROLES | Gestión de Roles | shield | /admin/roles | 2 | 1 |

## Organización por Grupos (según orden y URL)

### 🔵 GRUPO 1: Desvíos Ambientales (orden=1)
- **DASHBOARD** (id=1) - home - Sin URL
- **DESVIOS** (id=2) - /admin/registrar
- **ESTADISTICAS** (id=3) - /admin/estadisticas
- **MIS_REPORTES** (id=5) - /supervisor/desvios

### 🟢 GRUPO 2: Gestión de Residuos (orden=2)
- **GESTION_RESIDUOS** (id=16) - trash-2 - Sin URL (¿Padre?)
- **GENERACION_DIARIA** (id=17) - /admin/residuos/generacion
- **COMERCIALIZABLE** (id=18) - /admin/residuos/comercializable
- **DISPOSICION_MATPEL** (id=19) - /admin/residuos/matpel
- **COMPOSTAJE** (id=20) - /admin/residuos/compostaje
- **ROLES** (id=45) - /admin/roles

### 🟡 GRUPO 3: Compromisos (orden=3)
- **COMPROMISOS_REG** (id=26) - /admin/compromisos
- **COMPROMISOS_DASH** (id=29) - /admin/compromisos/dashboard
- **COMPROMISOS** (id=30) - /admin/compromisos/registro

### 🟣 GRUPO 4: Data Meteorológica (orden=4)
- **DATA_METRO_INFO** (id=27) - /admin/meteorologia
- **DATA_METRO_DASH** (id=31) - /admin/meteorologia/dashboard
- **DATA_METEOROLOGICA** (id=32) - /admin/meteorologia

### 🔴 GRUPO 5: Configuración (orden=5 y 50)
- **CONFIG_USUARIOS** (id=28) - /admin/configuracion/usuarios
- **CONFIGURACION** (id=4) - settings - Sin URL (¿Padre?)

### 🟠 GRUPO 6: Gestión de Aguas (orden=6 y 60)
- **GESTION_AGUAS** (id=33) - droplet - Sin URL (¿Padre?)
- **AGUAS_DASHBOARD** (id=34) - /admin/aguas/dashboard
- **MONITOREO_AMBIENTAL** (id=35) - /admin/aguas
- **REPORTE_ANA** (id=36) - /admin/ana

### 🔵 GRUPO 10: Desvíos Ambientales (Padre)
- **DESVIOS_AMB** (id=25) - alert-triangle - Sin URL

## 🤔 Observaciones

1. **Módulos sin URL** (posibles contenedores/padres):
   - DASHBOARD (id=1)
   - CONFIGURACION (id=4)
   - GESTION_RESIDUOS (id=16)
   - DESVIOS_AMB (id=25)
   - GESTION_AGUAS (id=33)

2. **Duplicados/Confusión**:
   - Hay 2 módulos llamados "Desvíos ambientales" (id=1 y id=25)
   - Hay 2 módulos de "Compromisos" con "Registro" (id=26 y id=30)
   - Hay 2 módulos de "Data Meteorológica" con "Información" (id=27 y id=32)

3. **Patrón de agrupación**:
   - Los módulos se agrupan por el **primer dígito del orden**
   - Orden 1.x = Desvíos
   - Orden 2.x = Residuos
   - Orden 3.x = Compromisos
   - Orden 4.x = Meteorología
   - Orden 5.x = Configuración
   - Orden 6.x = Aguas

## 💡 Propuesta de Flujo

### Opción A: Usar el campo "orden" para agrupar
```
Si orden empieza con 1 → Grupo "Desvíos Ambientales"
Si orden empieza con 2 → Grupo "Gestión de Residuos"
Si orden empieza con 3 → Grupo "Compromisos"
Si orden empieza con 4 → Grupo "Data Meteorológica"
Si orden empieza con 5 → Grupo "Configuración"
Si orden empieza con 6 → Grupo "Gestión de Aguas"
```

### Opción B: Usar prefijo de URL para agrupar
```
/admin/registrar* → Desvíos
/admin/residuos/* → Gestión de Residuos
/admin/compromisos/* → Compromisos
/admin/meteorologia/* → Data Meteorológica
/admin/configuracion/* → Configuración
/admin/aguas/* → Gestión de Aguas
/supervisor/* → Mis Reportes
```

### Opción C: Crear un nuevo campo "grupo"
Agregar un campo `grupo` a la tabla para identificar explícitamente a qué sección pertenece cada módulo.
