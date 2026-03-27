# 📚 Índice de Documentación - EcoSupervisor

## 📖 Documentación Disponible

### 🚀 Inicio y Configuración
- **[README.md](../README.md)** - Guía principal del proyecto
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Instrucciones de deployment

### 🔧 Funcionalidades
- **[ESTADO_ATRASADO.md](ESTADO_ATRASADO.md)** - Documentación del sistema de estados atrasados

## 📁 Estructura de Carpetas

```
ecosupervisor/
├── docs/              # Documentación (estás aquí)
├── sql/               # Scripts SQL (5 archivos esenciales)
├── scripts/           # Scripts Python auxiliares
├── routes/            # Módulos de rutas Flask
├── templates/         # Plantillas HTML
├── static/            # CSS, JS, imágenes
└── utils/             # Funciones auxiliares
```

## 🗂️ Archivos SQL Disponibles

Los siguientes scripts SQL están disponibles en la carpeta `sql/`:

1. **schema.sql** - Schema principal de la base de datos
2. **crear_sp_atrasado.sql** - Stored procedures para estados atrasados
3. **actualizar_sp_estadisticas.sql** - Stored procedures de estadísticas
4. **mejorar_sp_actualizar_registro.sql** - Mejoras a stored procedures
5. **fix_orden_atrasado.sql** - Fix para orden de estados

## 🔗 Enlaces Rápidos

### Para Desarrolladores
- [Estructura del Proyecto](../README.md#estructura-del-proyecto)
- [Configuración de Desarrollo](../README.md#desarrollo)
- [Variables de Entorno](../README.md#variables-de-entorno-env)

### Para Administradores
- [Instalación](../README.md#instalación)
- [Deployment](DEPLOYMENT.md)
- [Roles de Usuario](../README.md#roles-de-usuario)

### Para Mantenimiento
- [Scripts SQL](../sql/)
- [Scripts Python](../scripts/)

## 🧹 Limpieza Reciente

Se eliminaron archivos obsoletos de:
- ✅ Scripts SQL de migración y testing (20 archivos)
- ✅ Documentación de desarrollo temporal (10 archivos)
- ✅ Archivos de notas y análisis completados

El proyecto ahora está optimizado y contiene solo archivos necesarios para producción.

## 📝 Notas

- Toda la documentación está en formato Markdown
- Los archivos SQL están en la carpeta `sql/`
- Los scripts auxiliares están en la carpeta `scripts/`
- La documentación obsoleta ha sido eliminada

## 🔄 Última Actualización

**Fecha**: 27 de Marzo, 2026
**Versión**: 2.1
**Cambios**: Limpieza completa del proyecto - eliminados 31 archivos obsoletos
