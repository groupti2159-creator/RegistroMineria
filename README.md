# ecoSupervisor - Sistema de Gestión de Desvíos Ambientales

Sistema web para la gestión y seguimiento de desvíos ambientales en operaciones mineras.

## Características

- 📋 Registro y seguimiento de desvíos ambientales
- 👥 Gestión de usuarios (Administrador, Supervisor, Trabajador)
- 🖼️ Carga y validación de imágenes (evidencias y levantamientos)
- 📊 Dashboard con estadísticas en tiempo real
- 🔔 Sistema de notificaciones
- 📁 Exportación a Excel con imágenes
- 🗂️ Historial de reportes archivados
- 🌙 Modo oscuro/claro

## Tecnologías

- **Backend**: Flask (Python 3.12)
- **Base de Datos**: MySQL 8.0
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Despliegue**: Railway

## Estructura del Proyecto

```
ecosupervisor/
├── app.py                    # Aplicación principal
├── extensions.py             # Extensiones (MySQL)
├── requirements.txt          # Dependencias
├── Procfile                  # Comando de inicio (Railway)
├── runtime.txt               # Versión de Python
├── railway.json              # Configuración Railway
├── nixpacks.toml             # Build configuration
├── schema.sql                # Schema de base de datos
├── .env.example              # Ejemplo de variables de entorno
├── routes/                   # Rutas de la aplicación
│   ├── auth.py              # Autenticación
│   ├── admin.py             # Rutas de administrador
│   ├── supervisor.py        # Rutas de supervisor
│   └── shared.py            # Rutas compartidas
├── templates/                # Templates HTML
│   ├── base.html            # Template base
│   ├── auth/                # Templates de autenticación
│   ├── admin/               # Templates de administrador
│   ├── supervisor/          # Templates de supervisor
│   └── shared/              # Templates compartidos
├── static/                   # Archivos estáticos
│   ├── css/                 # Estilos
│   ├── js/                  # JavaScript
│   └── uploads/             # Imágenes subidas
│       ├── evidencias/      # Imágenes de evidencias
│       └── levantamientos/  # Imágenes de levantamientos
└── utils/                    # Utilidades
    ├── helpers.py           # Funciones auxiliares
    └── case_insensitive_dict.py  # Dict case-insensitive
```

## Instalación Local

### Requisitos
- Python 3.12+
- MySQL 8.0+
- pip

### Pasos

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd ecosupervisor
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar base de datos**
```bash
# Crear base de datos en MySQL
mysql -u root -p
CREATE DATABASE desvios_ambientales;
exit;

# Importar schema
mysql -u root -p desvios_ambientales < schema.sql
```

5. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# MYSQL_HOST=localhost
# MYSQL_USER=root
# MYSQL_PASSWORD=tu_password
# MYSQL_DB=desvios_ambientales
# MYSQL_PORT=3306
# SECRET_KEY=tu-clave-secreta
```

6. **Ejecutar la aplicación**
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## Usuarios de Prueba

### Administrador
- **DNI**: 12345678
- **Contraseña**: admin123

### Supervisor
- **DNI**: 87654321
- **Contraseña**: supervisor123

## Despliegue en Railway

Ver [DEPLOYMENT.md](DEPLOYMENT.md) para instrucciones detalladas de despliegue en Railway.

### Resumen rápido:
1. Crear servicio MySQL en Railway
2. Importar schema.sql
3. Crear servicio web desde GitHub
4. Configurar variables de entorno
5. Deploy automático

## Flujo de Trabajo

### Estados de Reportes
1. **Pendiente (EST001)**: Reporte creado, esperando levantamiento
2. **En Proceso (EST003)**: Supervisor subió imágenes, esperando validación
3. **Culminado (EST006)**: Admin aprobó imágenes, reporte completado

### Roles y Permisos

#### Administrador
- Crear, editar y archivar reportes
- Validar imágenes de levantamiento
- Ver dashboard con estadísticas
- Exportar reportes a Excel
- Acceso completo al sistema

#### Supervisor/Trabajador
- Ver reportes asignados
- Subir imágenes de levantamiento
- Ver historial personal
- Recibir notificaciones

## Características Técnicas

### Compatibilidad Linux/Windows
- Todas las referencias a base de datos en minúsculas
- Compatible con MySQL case-sensitive (Linux) y case-insensitive (Windows)
- Uso de `CaseInsensitiveDict` para acceso a resultados de stored procedures

### Seguridad
- Sesiones seguras con Flask
- Validación de roles en cada ruta
- Sanitización de inputs
- Protección contra SQL injection (uso de stored procedures)

### Optimizaciones
- Carga lazy de imágenes
- Compresión de imágenes al subir
- Paginación en tablas grandes
- Cache de consultas frecuentes

## Mantenimiento

### Backup de Base de Datos
```bash
mysqldump -u root -p desvios_ambientales > backup_$(date +%Y%m%d).sql
```

### Logs
Los logs de la aplicación se pueden ver en:
- Local: Terminal donde se ejecuta `python app.py`
- Railway: Dashboard > Logs

### Actualización de Dependencias
```bash
pip list --outdated
pip install --upgrade <package>
pip freeze > requirements.txt
```

## Solución de Problemas

### Error: "Table doesn't exist"
- Verificar que las tablas estén en minúsculas
- Reimportar schema.sql

### Error: "Connection refused"
- Verificar credenciales en .env
- Verificar que MySQL esté corriendo

### Imágenes no se cargan
- Verificar permisos en carpeta `static/uploads`
- Verificar que las rutas sean relativas

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto es privado y confidencial.

## Contacto

Para soporte o consultas, contactar al equipo de desarrollo.
