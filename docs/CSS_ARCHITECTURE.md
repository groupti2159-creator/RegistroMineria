# CSS Architecture - Modular & Reusable

## Objetivo
Transformar base.css (4461 líneas) en una arquitectura modular donde cada componente es reutilizable y mantenible.

## Estructura Propuesta

```
static/css/
├── base.css                          # Orquestador (solo @imports)
├── _variables.css                    # ✅ Variables globales (colores, espaciado, etc.)
├── _reset.css                        # ✅ Reset CSS básico
│
├── components/                       # Componentes reutilizables
│   ├── buttons.css                   # ✅ Todos los botones
│   ├── badges.css                    # ✅ Todos los badges
│   ├── cards.css                     # Cards genéricos
│   ├── modals.css                    # Sistema de modales
│   ├── forms.css                     # Inputs, selects, textareas
│   ├── tables.css                    # Tablas genéricas
│   ├── pagination.css                # Paginación
│   ├── alerts.css                    # Alertas y banners
│   └── notifications.css             # Notificaciones toast
│
├── layout/                           # Estructura de página
│   ├── layout.css                    # Layout principal
│   ├── sidebar.css                   # Sidebar y navegación
│   ├── topbar.css                    # Top bar
│   ├── proyecto-selector.css        # Selector de proyecto
│   └── responsive.css                # Media queries
│
├── utilities/                        # Utilidades
│   ├── animations.css                # Animaciones reutilizables
│   └── helpers.css                   # Clases helper
│
├── auth/                             # Módulo autenticación
│   ├── login.css                     # ✅ Login page
│   └── rol-selector.css              # ✅ Selector de rol
│
├── compromisos/                      # Módulo compromisos
│   └── registro.css                  # Registro de compromisos
│
├── configuracion/                    # Módulo configuración
│   ├── configuracion.css             # ✅ Dashboard configuración
│   └── usuarios.css                  # ✅ Gestión de usuarios
│
├── desvios_ambientales/              # Módulo desvíos
│   └── desvios_ambientales.css       # Desvíos ambientales
│
├── gestion_aguas/                    # Módulo aguas
│   ├── monitoreo_ambiental.css       # Monitoreo
│   └── reporte_ana.css               # Reportes ANA
│
└── gestion_residuos/                 # Módulo residuos
    ├── gestion_residuos.css          # General
    └── registro_diario.css           # ✅ Registro diario
```

## Principios

### 1. Single Responsibility
Cada archivo CSS tiene UNA responsabilidad clara:
- `buttons.css` → Solo botones
- `modals.css` → Solo modales
- `sidebar.css` → Solo sidebar

### 2. Reusabilidad
Los componentes son independientes y reutilizables:
```css
/* ✅ BIEN - Componente reutilizable */
.btn-primary { ... }

/* ❌ MAL - Específico de un módulo */
.compromisos-submit-button { ... }
```

### 3. Composición
Los módulos específicos USAN los componentes base:
```css
/* En compromisos/registro.css */
@import url('../components/buttons.css');
@import url('../components/modals.css');

/* Luego solo estilos específicos de compromisos */
.compromisos-table { ... }
```

### 4. Variables Centralizadas
Todas las variables en `_variables.css`:
```css
:root {
  --primary: #1a7a3c;
  --radius: 8px;
  /* etc */
}
```

### 5. Dark Mode Integrado
Cada componente incluye sus estilos dark:
```css
.btn-primary {
  background: var(--black);
}

[data-theme="dark"] .btn-primary {
  background: white;
}
```

## Plan de Implementación

### Fase 1: Core (✅ COMPLETADO)
- [x] _variables.css
- [x] _reset.css
- [x] components/buttons.css
- [x] components/badges.css

### Fase 2: Componentes Base (✅ COMPLETADO)
- [x] components/cards.css
- [x] components/modals.css
- [x] components/forms.css
- [x] components/tables.css
- [x] components/pagination.css
- [x] components/alerts.css
- [x] components/notifications.css

### Fase 3: Layout (✅ COMPLETADO)
- [x] layout/layout.css
- [x] layout/sidebar.css
- [x] layout/topbar.css
- [x] layout/proyecto-selector.css
- [x] layout/responsive.css

### Fase 4: Utilities (✅ COMPLETADO)
- [x] utilities/animations.css
- [x] utilities/helpers.css

### Fase 5: Integración (✅ COMPLETADO)
- [x] Crear nuevo base.css con @imports
- [x] Renombrar base.css antiguo a base-legacy.css
- [x] Actualizar templates para usar base.css
- [ ] Testing completo en todos los módulos
- [ ] Eliminar base-legacy.css después de validar

## Beneficios Esperados

1. **Mantenibilidad**: Cambiar un botón = editar 1 archivo
2. **Reusabilidad**: Componentes usables en cualquier módulo
3. **Performance**: Cargar solo CSS necesario
4. **Escalabilidad**: Agregar módulos sin tocar core
5. **Colaboración**: Equipos pueden trabajar en paralelo
6. **Testing**: Probar componentes aisladamente
7. **Documentación**: Cada archivo es auto-documentado

## Tamaño Estimado

- **Antes**: base.css = 4461 líneas
- **Después**: 
  - base.css (orquestador) = ~30 líneas
  - Componentes = ~2000 líneas
  - Layout = ~1500 líneas
  - Utilities = ~300 líneas
  - Módulos específicos = ~1500 líneas
  - **Total**: ~5330 líneas (distribuidas en ~25 archivos)

## Uso en Templates

### Antes:
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
```

### Después:
```html
<!-- Core siempre -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">

<!-- Módulo específico solo si se necesita -->
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/compromisos/registro.css') }}">
{% endblock %}
```

## Migración

1. Crear todos los archivos de componentes
2. Extraer código de base.css a componentes
3. Crear nuevo base.css con @imports
4. Renombrar base.css antiguo a base-legacy.css
5. Probar en desarrollo
6. Desplegar a producción
7. Eliminar base-legacy.css

## Notas

- Los @imports se resuelven en el servidor
- No hay impacto en performance del cliente
- Facilita el desarrollo y mantenimiento
- Permite tree-shaking en el futuro
