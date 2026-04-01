# CSS Modularization - Testing Checklist

## Estado: PENDIENTE DE TESTING

La modularización CSS está **100% completada** a nivel de código. Este documento lista todas las verificaciones necesarias antes de eliminar `base-legacy.css`.

## Pre-requisitos

- [x] Todos los módulos CSS creados
- [x] Archivo `base.css` orquestador creado
- [x] Archivo `base-legacy.css` respaldado
- [x] Template `base.html` configurado correctamente
- [ ] Servidor de desarrollo corriendo

## Testing por Módulo

### 1. Autenticación
- [ ] **Login Page** (`auth/login.css`)
  - [ ] Formulario de login se ve correctamente
  - [ ] Botones funcionan
  - [ ] Responsive en móvil
  - [ ] Dark mode funciona

- [ ] **Selector de Rol** (`auth/rol-selector.css`)
  - [ ] Cards de roles se ven bien
  - [ ] Hover effects funcionan
  - [ ] Selección visual correcta

### 2. Layout General
- [ ] **Sidebar** (`layout/sidebar.css`)
  - [ ] Navegación se despliega correctamente
  - [ ] Submenús funcionan
  - [ ] Iconos se ven bien
  - [ ] Animaciones suaves
  - [ ] Badges de notificación visibles
  - [ ] Dark mode correcto

- [ ] **Top Bar** (`layout/topbar.css`)
  - [ ] Título de página visible
  - [ ] Selector de proyecto funciona
  - [ ] Notificaciones se despliegan
  - [ ] Responsive en móvil

- [ ] **Layout Principal** (`layout/layout.css`)
  - [ ] Estructura general correcta
  - [ ] Espaciado apropiado
  - [ ] Scroll funciona

- [ ] **Responsive** (`layout/responsive.css`)
  - [ ] Desktop (>1024px) ✓
  - [ ] Tablet (768px-1024px) ✓
  - [ ] Móvil (480px-768px) ✓
  - [ ] Móvil pequeño (<480px) ✓
  - [ ] Menú hamburguesa funciona
  - [ ] Sidebar se oculta en móvil

### 3. Componentes Base

- [ ] **Botones** (`components/buttons.css`)
  - [ ] btn-primary funciona
  - [ ] btn-secondary funciona
  - [ ] btn-danger funciona
  - [ ] btn-export funciona
  - [ ] btn-icon funciona
  - [ ] Estados hover correctos
  - [ ] Estados disabled correctos
  - [ ] Dark mode correcto

- [ ] **Badges** (`components/badges.css`)
  - [ ] badge-blue visible
  - [ ] badge-green visible
  - [ ] badge-yellow visible
  - [ ] badge-red visible
  - [ ] badge-gray visible
  - [ ] Estados (pendiente, culminado, etc.) correctos
  - [ ] Dark mode correcto

- [ ] **Cards** (`components/cards.css`)
  - [ ] Cards básicos se ven bien
  - [ ] Stat cards funcionan
  - [ ] Chart cards funcionan
  - [ ] KPI cards funcionan
  - [ ] Quick actions funcionan
  - [ ] Hover effects correctos
  - [ ] Dark mode correcto

- [ ] **Modales** (`components/modals.css`)
  - [ ] Modal se abre correctamente
  - [ ] Overlay funciona
  - [ ] Botón cerrar funciona
  - [ ] Scroll interno funciona
  - [ ] Animación de entrada suave
  - [ ] Dark mode correcto

- [ ] **Formularios** (`components/forms.css`)
  - [ ] Inputs se ven bien
  - [ ] Selects funcionan
  - [ ] Textareas funcionan
  - [ ] Validación visual funciona
  - [ ] File upload funciona
  - [ ] Image preview funciona
  - [ ] Estados focus correctos
  - [ ] Dark mode correcto

- [ ] **Tablas** (`components/tables.css`)
  - [ ] data-table se ve bien
  - [ ] Hover en filas funciona
  - [ ] Badges en celdas visibles
  - [ ] Action buttons funcionan
  - [ ] Scroll horizontal en móvil
  - [ ] Dark mode correcto

- [ ] **Paginación** (`components/pagination.css`)
  - [ ] Botones de navegación funcionan
  - [ ] Números de página visibles
  - [ ] Página activa destacada
  - [ ] Estados disabled correctos
  - [ ] Responsive en móvil

- [ ] **Notificaciones** (`components/notifications.css`)
  - [ ] Toast notifications aparecen
  - [ ] Animación de entrada/salida
  - [ ] Auto-dismiss funciona
  - [ ] Diferentes tipos (success, error, info)
  - [ ] Dark mode correcto

- [ ] **Alertas** (`components/alerts.css`)
  - [ ] alert-success visible
  - [ ] alert-error visible
  - [ ] alert-info visible
  - [ ] Botón cerrar funciona
  - [ ] Dark mode correcto

### 4. Módulos Específicos

- [ ] **Compromisos** (`compromisos/registro.css`)
  - [ ] Tabla de compromisos se ve bien
  - [ ] Modal de registro funciona
  - [ ] Filtros funcionan
  - [ ] Evidencias se muestran correctamente
  - [ ] Dark mode correcto

- [ ] **Desvíos Ambientales** (`desvios_ambientales/desvios_ambientales.css`)
  - [ ] Dashboard se ve bien
  - [ ] Formulario de registro funciona
  - [ ] Estadísticas visibles
  - [ ] Dark mode correcto

- [ ] **Gestión de Aguas** 
  - [ ] **Monitoreo** (`gestion_aguas/monitoreo_ambiental.css`)
    - [ ] Tabla de monitoreo funciona
    - [ ] Modal de registro funciona
    - [ ] Dark mode correcto
  
  - [ ] **Reporte ANA** (`gestion_aguas/reporte_ana.css`)
    - [ ] Formulario de reporte funciona
    - [ ] Validaciones visuales correctas
    - [ ] Dark mode correcto

- [ ] **Gestión de Residuos**
  - [ ] **General** (`gestion_residuos/gestion_residuos.css`)
    - [ ] Dashboard funciona
    - [ ] Navegación correcta
    - [ ] Dark mode correcto
  
  - [ ] **Registro Diario** (`gestion_residuos/registro_diario.css`)
    - [ ] Modal de registro funciona
    - [ ] Grid de plantas funciona
    - [ ] Cálculos automáticos funcionan
    - [ ] Dark mode correcto

- [ ] **Configuración**
  - [ ] **Dashboard** (`configuracion/configuracion.css`)
    - [ ] Cards de configuración visibles
    - [ ] Navegación funciona
    - [ ] Dark mode correcto
  
  - [ ] **Usuarios** (`configuracion/usuarios.css`)
    - [ ] Tabla de usuarios funciona
    - [ ] Modal de edición funciona
    - [ ] Gestión de roles funciona
    - [ ] Dark mode correcto

### 5. Utilidades

- [ ] **Animaciones** (`utilities/animations.css`)
  - [ ] Fade in funciona
  - [ ] Slide in funciona
  - [ ] Toast animations funcionan
  - [ ] Ripple effect funciona
  - [ ] Spin animation funciona

- [ ] **Helpers** (`utilities/helpers.css`)
  - [ ] Empty states se ven bien
  - [ ] Loading states funcionan
  - [ ] Activity list funciona
  - [ ] Stats list funciona

### 6. Dark Mode

- [ ] **Todos los componentes en dark mode**
  - [ ] Variables de color correctas
  - [ ] Contraste adecuado
  - [ ] Legibilidad mantenida
  - [ ] Transiciones suaves
  - [ ] Toggle funciona

### 7. Cross-Browser Testing

- [ ] **Chrome** (versión 88+)
  - [ ] Desktop
  - [ ] Móvil

- [ ] **Firefox** (versión 85+)
  - [ ] Desktop
  - [ ] Móvil

- [ ] **Safari** (versión 14+)
  - [ ] Desktop
  - [ ] iOS

- [ ] **Edge** (versión 88+)
  - [ ] Desktop

### 8. Performance

- [ ] **Carga inicial**
  - [ ] Tiempo de carga < 2s
  - [ ] No hay FOUC (Flash of Unstyled Content)
  - [ ] Fonts cargan correctamente

- [ ] **Navegación**
  - [ ] Cambios de página suaves
  - [ ] No hay lag en animaciones
  - [ ] Scroll suave

## Validación Técnica

### CSS Validation
```bash
# Validar sintaxis CSS
npx stylelint "static/css/**/*.css"
```

### Verificar @imports
```bash
# Verificar que todos los @imports se resuelven
# Abrir DevTools > Network > CSS
# Verificar que no hay 404s
```

### Verificar tamaño de archivos
```bash
# Comparar tamaño total
Get-ChildItem -Path "static/css" -Filter "*.css" -Recurse | 
  Measure-Object -Property Length -Sum
```

## Checklist de Limpieza

Una vez que TODO el testing esté ✅:

- [ ] Eliminar `base-legacy.css`
- [ ] Optimizar `dark_mode.css` (eliminar duplicaciones)
- [ ] Minificar CSS para producción
- [ ] Actualizar documentación
- [ ] Commit final con mensaje descriptivo

## Rollback Plan

Si algo falla durante el testing:

1. Renombrar `base.css` a `base-modular.css`
2. Renombrar `base-legacy.css` a `base.css`
3. Actualizar `base.html` para usar `base-legacy.css`
4. Investigar y corregir el problema
5. Volver a intentar

## Comandos Útiles

### Iniciar servidor de desarrollo
```bash
cd RegistroMineria
python app.py
```

### Ver logs en tiempo real
```bash
# En PowerShell
Get-Content -Path "logs/app.log" -Wait -Tail 50
```

### Limpiar caché del navegador
```
Ctrl + Shift + R (Chrome/Firefox)
Cmd + Shift + R (Safari)
```

## Notas

- Probar en modo incógnito para evitar caché
- Usar DevTools para inspeccionar estilos aplicados
- Verificar que no hay estilos inline que sobrescriban
- Comprobar que las variables CSS se resuelven correctamente

---

**Creado**: 31 de Marzo, 2026  
**Estado**: 📋 PENDIENTE DE TESTING  
**Prioridad**: ALTA  
**Tiempo estimado**: 2-3 horas
