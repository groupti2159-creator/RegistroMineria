# Guía de Despliegue en Railway

## Requisitos Previos
- Cuenta en [Railway](https://railway.app)
- Base de datos MySQL en Railway ya configurada
- Dump de la base de datos con todas las tablas y stored procedures en minúsculas

## Pasos para Desplegar

### 1. Preparar la Base de Datos
1. Crear un servicio MySQL en Railway
2. Importar el dump de la base de datos (schema.sql)
3. Verificar que todas las tablas y stored procedures estén en minúsculas
4. Anotar las credenciales de conexión (host, port, user, password, database)

### 2. Configurar el Proyecto en Railway

#### Opción A: Desde GitHub
1. Subir el proyecto a un repositorio de GitHub
2. En Railway, crear un nuevo proyecto
3. Seleccionar "Deploy from GitHub repo"
4. Elegir el repositorio

#### Opción B: Desde CLI
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Vincular con el proyecto
railway link
```

### 3. Configurar Variables de Entorno
En Railway, ir a Variables y agregar:

```
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-aqui-cambiar-esto
MYSQL_HOST=tu-host.proxy.rlwy.net
MYSQL_USER=root
MYSQL_PASSWORD=tu-password
MYSQL_DB=desvios_ambientales
MYSQL_PORT=12842
UPLOAD_FOLDER=static/uploads
MAX_IMAGES_PER_REGISTRO=5
```

**IMPORTANTE**: Cambiar `SECRET_KEY` por una clave segura generada aleatoriamente.

### 4. Desplegar
Railway detectará automáticamente:
- `requirements.txt` para instalar dependencias
- `Procfile` para el comando de inicio
- `nixpacks.toml` para configuración de build

El despliegue se iniciará automáticamente.

### 5. Verificar el Despliegue
1. Esperar a que el build termine (ver logs en Railway)
2. Abrir la URL generada por Railway
3. Probar el login con las credenciales:
   - Admin: DNI `12345678`, password `admin123`
   - Supervisor: DNI `87654321`, password `supervisor123`

## Estructura de Archivos para Railway

```
ecosupervisor/
├── app.py                 # Aplicación principal Flask
├── extensions.py          # Extensiones (MySQL)
├── requirements.txt       # Dependencias Python
├── Procfile              # Comando de inicio
├── runtime.txt           # Versión de Python
├── railway.json          # Configuración Railway
├── nixpacks.toml         # Configuración de build
├── .env.example          # Ejemplo de variables de entorno
├── .gitignore            # Archivos a ignorar en Git
├── schema.sql            # Schema de base de datos
├── routes/               # Rutas de la aplicación
├── templates/            # Templates HTML
├── static/               # Archivos estáticos (CSS, JS, imágenes)
├── utils/                # Utilidades (helpers, case_insensitive_dict)
└── models/               # Modelos (vacío por ahora)
```

## Solución de Problemas

### Error: "Table doesn't exist"
- Verificar que todas las tablas estén en minúsculas en MySQL
- Railway usa Linux (case-sensitive), Windows no

### Error: "Connection refused"
- Verificar las variables de entorno (MYSQL_HOST, MYSQL_PORT, etc.)
- Verificar que el servicio MySQL esté activo en Railway

### Error: "Module not found"
- Verificar que `requirements.txt` esté completo
- Revisar los logs de build en Railway

### Imágenes no se cargan
- Verificar que la carpeta `static/uploads` exista
- En Railway, las imágenes se pierden en cada deploy (usar almacenamiento externo como S3 para producción)

## Notas Importantes

1. **Almacenamiento de Imágenes**: Railway usa almacenamiento efímero. Las imágenes subidas se perderán en cada redeploy. Para producción, considerar usar:
   - AWS S3
   - Cloudinary
   - Railway Volumes (persistente)

2. **Base de Datos**: Asegurarse de que el dump tenga:
   - Todas las tablas en minúsculas
   - Todos los stored procedures en minúsculas
   - Referencias a tablas dentro de los SP en minúsculas

3. **Seguridad**:
   - Cambiar `SECRET_KEY` en producción
   - No subir `.env` a Git (ya está en `.gitignore`)
   - Usar contraseñas fuertes para usuarios

4. **Monitoreo**:
   - Revisar logs en Railway regularmente
   - Configurar alertas para errores críticos

## Comandos Útiles

```bash
# Ver logs en tiempo real
railway logs

# Ejecutar comando en el contenedor
railway run python

# Abrir shell en el contenedor
railway shell

# Ver variables de entorno
railway variables

# Redeploy manual
railway up
```

## Contacto y Soporte
Para problemas o preguntas, revisar los logs de Railway y verificar la configuración de variables de entorno.
