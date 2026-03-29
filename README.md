# 🌿 EcoSupervisor

Sistema de gestión ambiental para supervisión de desvíos, residuos, meteorología y más.

## 📋 Descripción

EcoSupervisor es una aplicación web desarrollada en Flask para la gestión integral de:
- Desvíos ambientales
- Gestión de residuos (generación, comercializable, compostaje, MATPEL)
- Monitoreo meteorológico
- Gestión de aguas
- Compromisos ambientales
- Sistema de usuarios y roles

## 🚀 Inicio Rápido

### Requisitos
- Python 3.8+
- MySQL 5.7+
- pip

### Instalación

1. Clonar el repositorio
```bash
git clone <repo-url>
cd ecosupervisor
```

2. Instalar dependencias
```bash
pip install -r requirements.txt
```

3. Configurar base de datos
```bash
# Crear base de datos
mysql -u root -p -e "CREATE DATABASE ecosupervisor CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Importar esquema
mysql -u root -p ecosupervisor < sql/schema.sql

# Crear sistema de usuarios
mysql -u root -p ecosupervisor < sql/crear_sistema_usuarios_completo.sql

# Crear roles
mysql -u root -p ecosupervisor < sql/crear_nuevos_roles.sql
```

4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. Ejecutar aplicación
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

## 📁 Estructura del Proyecto

```
ecosupervisor/
├── app.py                  # Aplicación principal Flask
├── config.py               # Configuración general
├── config_proyectos.py     # Configuración de proyectos
├── extensions.py           # Extensiones (MySQL, etc.)
├── requirements.txt        # Dependencias Python
│
├── routes/                 # Módulos de rutas
│   ├── admin.py           # Administración
│   ├── auth.py            # Autenticación
│   ├── desvios_ambientales.py
│   ├── gestion_residuos.py
│   ├── supervisor.py
│   └── ...
│
├── templates/             # Plantillas HTML
│   ├── base.html
│   ├── admin/
│   ├── auth/
│   ├── desvios_ambientales/
│   ├── gestion_residuos/
│   └── ...
│
├── static/                # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
│
├── utils/                 # Utilidades
│   └── helpers.py
│
├── sql/                   # Scripts SQL
│   ├── schema.sql
│   ├── crear_sistema_usuarios_completo.sql
│   └── ...
│
├── scripts/               # Scripts Python auxiliares
│   └── actualizar_estados_atrasados.py
│
└── docs/                  # Documentación
    ├── DEPLOYMENT.md
    ├── ESTADO_ATRASADO.md
    └── ...
```

## 👥 Roles de Usuario

- **Administrador**: Acceso completo al sistema
- **Supervisor**: Gestión de desvíos y validación de levantamientos
- **Trabajador**: Visualización y subida de evidencias
- **Automatizador**: Acceso a APIs y automatizaciones

## 🔧 Configuración

### Variables de Entorno (.env)

```env
# Base de datos
MYSQL_HOST=localhost
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_contraseña
MYSQL_DB=ecosupervisor

# Flask
SECRET_KEY=tu_clave_secreta_aqui
FLASK_ENV=development

# Uploads
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### Configuración de Proyectos

Editar `config_proyectos.py` para configurar los proyectos disponibles.

## 📚 Documentación

- [Guía de Deployment](docs/DEPLOYMENT.md)
- [Estado Atrasado](docs/ESTADO_ATRASADO.md)
- [Limpieza del Proyecto](docs/LIMPIEZA_PROYECTO.md)

## 🛠️ Desarrollo

### Ejecutar en modo desarrollo
```bash
export FLASK_ENV=development
python app.py
```

### Ejecutar tests
```bash
pytest
```

## 🚢 Deployment

Ver [DEPLOYMENT.md](docs/DEPLOYMENT.md) para instrucciones detalladas de deployment en:
- Railway
- Heroku
- Servidor propio

## 📝 Licencia

[Especificar licencia]

## 👨‍💻 Autores

[Especificar autores]

## 🤝 Contribuir

[Instrucciones para contribuir]
