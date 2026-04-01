# Guía para Desarrolladores - CSS Modular

## Introducción

Este proyecto utiliza una arquitectura CSS modular basada en principios SOLID. Esta guía te ayudará a trabajar eficientemente con el nuevo sistema.

## Estructura de Archivos

```
static/css/
├── base.css                    # ⚠️ NO EDITAR - Solo @imports
├── _variables.css              # Variables globales
├── _reset.css                  # Reset CSS
├── components/                 # Componentes reutilizables
├── layout/                     # Estructura de página
├── utilities/                  # Utilidades y helpers
└── [modulo]/                   # Módulos específicos
```

## Reglas de Oro

### 1. ⚠️ NUNCA editar `base.css`
Este archivo es solo un orquestador. Para agregar estilos:
- Edita el componente existente, O
- Crea un nuevo módulo específico

### 2. ✅ Usar variables CSS
```css
/* ❌ MAL */
.mi-boton {
  background: #1a7a3c;
  color: #ffffff;
}

/* ✅ BIEN */
.mi-boton {
  background: var(--primary);
  color: var(--white);
}
```

### 3. ✅ Seguir la convención de nombres
```css
/* Componentes genéricos */
.btn-primary { }
.card { }
.modal { }

/* Módulos específicos */
.compromisos-table { }
.residuos-grid { }
.aguas-form { }
```

### 4. ✅ Incluir dark mode
```css
.mi-componente {
  background: var(--bg-card);
  color: var(--text);
}

[data-theme="dark"] .mi-componente {
  background: var(--bg-card); /* Variable se adapta automáticamente */
}
```

## Casos de Uso Comunes

### Caso 1: Modificar un botón existente

**Ubicación**: `components/buttons.css`

```css
/* Agregar nuevo estilo de botón */
.btn-success {
  background: var(--pastel-green);
  color: var(--text-green);
  border: 1px solid var(--border);
}

.btn-success:hover {
  background: var(--text-green);
  color: white;
}

[data-theme="dark"] .btn-success {
  background: rgba(34, 197, 94, 0.15);
  color: #86efac;
}
```

### Caso 2: Crear un nuevo módulo

**Ejemplo**: Módulo de Meteorología

1. Crear archivo: `static/css/meteorologia/dashboard.css`

```css
/* ═══════════════════════════════════════════════════════
   METEOROLOGÍA — Dashboard
═══════════════════════════════════════════════════════ */

.meteo-dashboard {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.meteo-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
}

/* Dark mode */
[data-theme="dark"] .meteo-card {
  background: #252a3a;
  border-color: #353d55;
}

/* Responsive */
@media (max-width: 768px) {
  .meteo-dashboard {
    grid-template-columns: 1fr;
  }
}
```

2. Incluir en template:

```html
{% extends "base.html" %}

{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/meteorologia/dashboard.css') }}">
{% endblock %}

{% block content %}
<div class="meteo-dashboard">
  <div class="meteo-card">...</div>
</div>
{% endblock %}
```

### Caso 3: Agregar una nueva variable

**Ubicación**: `_variables.css`

```css
:root {
  /* Agregar al final de las variables existentes */
  --meteo-blue: #0ea5e9;
  --meteo-blue-light: #e0f2fe;
}

[data-theme="dark"] {
  --meteo-blue: #38bdf8;
  --meteo-blue-light: rgba(14, 165, 233, 0.15);
}
```

### Caso 4: Modificar el layout

**Ubicación**: `layout/sidebar.css`, `layout/topbar.css`, etc.

```css
/* Agregar nuevo item al sidebar */
.nav-item.meteo {
  /* Estilos específicos si es necesario */
}
```

### Caso 5: Crear un componente reutilizable

**Ubicación**: `components/[nombre].css`

**Ejemplo**: Componente de Timeline

1. Crear `components/timeline.css`:

```css
/* ═══════════════════════════════════════════════════════
   TIMELINE — Componente de línea de tiempo
═══════════════════════════════════════════════════════ */

.timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  position: relative;
  padding-left: 2rem;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border);
}

.timeline-item {
  position: relative;
  padding: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -2.5rem;
  top: 1.5rem;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--primary);
  border: 2px solid var(--bg);
}

/* Dark mode */
[data-theme="dark"] .timeline-item {
  background: #252a3a;
  border-color: #353d55;
}
```

2. Agregar import en `base.css`:

```css
/* En la sección de COMPONENTES REUTILIZABLES */
@import url('components/timeline.css');
```

3. Usar en cualquier módulo:

```html
<div class="timeline">
  <div class="timeline-item">
    <h4>Evento 1</h4>
    <p>Descripción...</p>
  </div>
  <div class="timeline-item">
    <h4>Evento 2</h4>
    <p>Descripción...</p>
  </div>
</div>
```

## Debugging

### Ver qué estilos se están aplicando

1. Abrir DevTools (F12)
2. Inspeccionar elemento
3. Ver pestaña "Styles" o "Computed"
4. Verificar de qué archivo viene cada regla

### Verificar que los @imports funcionan

1. Abrir DevTools > Network
2. Filtrar por CSS
3. Verificar que todos los archivos cargan (200 OK)
4. No debe haber 404s

### Problemas comunes

#### Estilos no se aplican
- ✅ Verificar que el archivo CSS está importado en `base.css`
- ✅ Verificar que el template incluye `base.css`
- ✅ Limpiar caché del navegador (Ctrl+Shift+R)
- ✅ Verificar especificidad CSS

#### Variables no funcionan
- ✅ Verificar que están definidas en `_variables.css`
- ✅ Usar sintaxis correcta: `var(--nombre-variable)`
- ✅ Verificar que `_variables.css` se importa primero

#### Dark mode no funciona
- ✅ Verificar que el HTML tiene `data-theme="dark"`
- ✅ Usar variables CSS en lugar de colores hardcoded
- ✅ Definir estilos dark en `[data-theme="dark"]`

## Best Practices

### 1. Mantén los archivos pequeños
- Máximo 400-500 líneas por archivo
- Si crece mucho, considera dividirlo

### 2. Documenta tus cambios
```css
/* ═══════════════════════════════════════════════════════
   SECCIÓN — Descripción
═══════════════════════════════════════════════════════ */

/* Subsección */
.mi-clase {
  /* Comentario si es necesario */
}
```

### 3. Usa nombres descriptivos
```css
/* ❌ MAL */
.box1 { }
.thing { }
.stuff { }

/* ✅ BIEN */
.meteo-card { }
.timeline-item { }
.user-avatar { }
```

### 4. Agrupa propiedades relacionadas
```css
.mi-clase {
  /* Layout */
  display: flex;
  flex-direction: column;
  gap: 1rem;
  
  /* Apariencia */
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  
  /* Tipografía */
  font-size: .85rem;
  color: var(--text);
  
  /* Transiciones */
  transition: all .2s ease;
}
```

### 5. Mobile-first cuando sea posible
```css
/* Base (móvil) */
.grid {
  grid-template-columns: 1fr;
}

/* Desktop */
@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## Workflow Recomendado

### Para cambios pequeños
1. Identificar el archivo correcto
2. Hacer el cambio
3. Refrescar navegador (Ctrl+Shift+R)
4. Verificar en DevTools
5. Commit

### Para nuevos módulos
1. Crear archivo en carpeta apropiada
2. Escribir estilos con estructura estándar
3. Agregar import en `base.css` (si es componente)
4. Incluir en template (si es módulo específico)
5. Probar en diferentes breakpoints
6. Probar en dark mode
7. Commit con mensaje descriptivo

### Para refactoring
1. Identificar código duplicado
2. Extraer a componente reutilizable
3. Actualizar todos los usos
4. Probar exhaustivamente
5. Eliminar código viejo
6. Commit

## Comandos Útiles

### Ver todos los archivos CSS
```powershell
Get-ChildItem -Path "static/css" -Filter "*.css" -Recurse | 
  Select-Object Name, @{Name="Lines";Expression={(Get-Content $_.FullName | Measure-Object -Line).Lines}}
```

### Buscar un selector
```powershell
Get-ChildItem -Path "static/css" -Filter "*.css" -Recurse | 
  Select-String -Pattern ".mi-clase"
```

### Contar líneas totales
```powershell
(Get-ChildItem -Path "static/css" -Filter "*.css" -Recurse | 
  Get-Content | Measure-Object -Line).Lines
```

## Recursos

- **Documentación**: `docs/CSS_ARCHITECTURE.md`
- **Estadísticas**: `docs/CSS_STATS.md`
- **Testing**: `docs/CSS_TESTING_CHECKLIST.md`
- **Variables disponibles**: `static/css/_variables.css`

## Preguntas Frecuentes

### ¿Puedo usar CSS inline?
❌ No. Usa clases CSS siempre que sea posible.

### ¿Puedo usar !important?
⚠️ Solo en casos extremos. Generalmente indica un problema de especificidad.

### ¿Dónde pongo estilos temporales para testing?
En el módulo específico del feature que estás desarrollando.

### ¿Cómo agrego un nuevo breakpoint?
Edita `layout/responsive.css` y sigue el patrón existente.

### ¿Puedo usar preprocesadores (SASS, LESS)?
No por ahora. El sistema usa CSS vanilla con variables nativas.

### ¿Cómo contribuyo un nuevo componente?
1. Crea el archivo en `components/`
2. Sigue la estructura estándar
3. Agrega import en `base.css`
4. Documenta su uso
5. Crea PR

---

**Última actualización**: 31 de Marzo, 2026  
**Versión**: 1.0.0  
**Mantenedor**: Equipo de Desarrollo
