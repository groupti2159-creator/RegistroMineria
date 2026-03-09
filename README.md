# 🌍 ecoSupervisor — Sistema de Monitoreo Ambiental

## Descripción
Sistema web para gestión de desvíos ambientales con roles de Administrador, Supervisor y Trabajador.

## Tecnologías
- **Backend:** Python 3.10+ / Flask 3.0
- **Frontend:** Jinja2 + HTML/CSS/JS puro
- **Base de datos:** MySQL / MariaDB
- **Exportación:** openpyxl (Excel)

## Instalación

### 1. Clonar e instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar base de datos
Edita el archivo `.env`:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=TU_PASSWORD
MYSQL_DB=desvios_ambientales
```

### 3. Ejecutar el script SQL
En MySQL Workbench o terminal:
```sql
source schema.sql;
```
Esto crea la base de datos, tablas, stored procedures y datos iniciales.

### 4. Ejecutar la aplicación
```bash
python app.py
```
Abre: http://localhost:5000

## Usuarios de prueba
| DNI      | Contraseña | Rol            |
|----------|-----------|----------------|
| 12345678 | admin123  | Administrador  |
| 87654321 | sup123    | Supervisor     |
| 11223344 | trab123   | Trabajador     |

## Estructura del proyecto
```
ecosupervisor/
├── app.py                    # App principal Flask
├── schema.sql                # BD + Stored Procedures
├── .env                      # Variables de entorno
├── requirements.txt
├── routes/
│   ├── auth.py               # Login/logout
│   ├── admin.py              # Panel administrador
│   ├── supervisor.py         # Panel supervisor/trabajador
│   └── shared.py             # API notificaciones
├── utils/
│   └── helpers.py            # Funciones auxiliares
├── templates/
│   ├── base.html             # Layout principal
│   ├── auth/login.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── desvios.html
│   │   └── historial.html
│   ├── supervisor/
│   │   ├── desvios.html
│   │   └── historial.html
│   └── shared/
│       └── tabla_registros.html
└── static/
    ├── css/main.css
    ├── js/
    │   ├── main.js
    │   └── desvios.js
    └── uploads/
        ├── evidencias/
        └── levantamientos/
```

## Flujo del sistema
1. **Admin** crea reporte → estado **PENDIENTE**
2. **Supervisor/Trabajador** ve el reporte y sube imágenes de levantamiento → estado **EN PROCESO**
3. **Admin** valida imágenes:
   - ✅ Aprueba → estado **CULMINADO**
   - ❌ Rechaza → vuelve a **PENDIENTE** (supervisor puede reintentar)
4. **Admin** archiva el registro culminado → aparece en **Historial**

## Módulos
- 🏠 **Dashboard** (Admin): estadísticas generales
- ⚠️ **Desvíos Ambientales**: tabla, crear/editar/archivar reportes
- 🗂️ **Historial**: registros archivados (Admin ve todos, Supervisor ve los suyos)
- 📊 **Estadísticas**: módulo preparado (próximamente)
- 🔔 **Notificaciones**: en tiempo real al cambiar estados

## Notas técnicas
- Contraseñas encriptadas con **MD5**
- Máximo **5 imágenes** por tipo (evidencia / levantamiento)
- Todos los accesos a BD via **Stored Procedures**
- Modo oscuro incluido
- Exportación a Excel (.xlsx) con formato
