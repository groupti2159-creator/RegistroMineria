# 🚀 Implementación de Menú 100% Dinámico

## 📋 Resumen

Te he preparado todo para que el sidebar sea **completamente dinámico** desde la base de datos. Cualquier cambio que hagas en `tbl_modulo` (nombre, icono, URL, orden) se reflejará automáticamente en la aplicación.

---

## 🎯 Alternativas que te propuse:

### ✅ **Alternativa 1: Usar `idmodulopadre` (RECOMENDADA)**

**Ventajas:**
- Estructura estándar y escalable
- Fácil de mantener
- Ya tienes el código listo en `base.html`

**Cómo funciona:**
```
DESVIOS_AMB (padre) → sin idmodulopadre
  ├─ DASHBOARD (hijo) → idmodulopadre = 25
  ├─ DESVIOS (hijo) → idmodulopadre = 25
  └─ ESTADISTICAS (hijo) → idmodulopadre = 25
```

**Para cambiar el nombre:**
```sql
UPDATE tbl_modulo SET nombre = 'Desvíos SSOMA' WHERE idmodulo = 25;
```
¡Listo! Se refleja automáticamente.

---

## 📝 Pasos para implementar:

### **Paso 1: Ejecutar el script de implementación**

```bash
python implementar_menu_dinamico.py
```

Este script:
1. ✅ Establece las relaciones padre-hijo correctamente
2. ✅ Actualiza los nombres de los grupos
3. ✅ Elimina módulos duplicados
4. ✅ Verifica la estructura final

### **Paso 2: Reemplazar el código del menú en base.html**

Busca en `templates/base.html` la sección que empieza con:
```jinja2
{# ── DESVÍOS AMBIENTALES ── #}
```

Y reemplázala COMPLETA (hasta antes de `</nav>`) con este código:

```jinja2
        {# ══════════════════════════════════════════════════════════════════════ #}
        {# MENÚ 100% DINÁMICO DESDE BASE DE DATOS                              #}
        {# Los nombres, iconos y URLs se cargan automáticamente desde tbl_modulo #}
        {# ══════════════════════════════════════════════════════════════════════ #}
        
        {% for modulo in session.get('modulos', []) %}
          {# Verificar si el usuario tiene acceso al módulo padre #}
          {% if modulo.get('codigo') in accesos %}
            
            {# CASO 1: Módulo con hijos (grupo desplegable) #}
            {% if modulo.get('hijos') and modulo.get('hijos')|length > 0 %}
              {% set hijos_accesibles = [] %}
              
              {# Filtrar solo los hijos a los que el usuario tiene acceso #}
              {% for hijo in modulo.get('hijos', []) %}
                {% if hijo.get('codigo') in accesos %}
                  {% set _ = hijos_accesibles.append((
                    hijo.get('nombre', 'Sin nombre'),
                    hijo.get('url', '#'),
                    hijo.get('icono', 'circle')
                  )) %}
                {% endif %}
              {% endfor %}
              
              {# Solo mostrar el grupo si tiene al menos un hijo accesible #}
              {% if hijos_accesibles|length > 0 %}
                {{ nav_group(
                  modulo.get('icono', 'circle'),
                  modulo.get('nombre', 'Módulo'),
                  hijos_accesibles
                ) }}
              {% endif %}
              
            {# CASO 2: Módulo sin hijos (item simple) #}
            {% elif modulo.get('url') %}
              <a href="{{ modulo.get('url') }}" class="nav-item {% if request.path == modulo.get('url') %}active{% endif %}">
                <span class="nav-icon"><i data-feather="{{ modulo.get('icono', 'circle') }}"></i></span>
                <span>{{ modulo.get('nombre', 'Módulo') }}</span>
              </a>
            {% endif %}
            
          {% endif %}
        {% endfor %}
```

### **Paso 3: Probar**

1. Reinicia la aplicación Flask
2. Cierra sesión y vuelve a iniciar sesión
3. Verás el menú generado dinámicamente

---

## 💡 Ejemplos de uso después de implementar:

### Cambiar nombre de un grupo:
```sql
UPDATE tbl_modulo SET nombre = 'Desvíos SSOMA' WHERE idmodulo = 25;
```

### Cambiar icono:
```sql
UPDATE tbl_modulo SET icono = 'shield' WHERE idmodulo = 25;
```

### Cambiar orden de aparición:
```sql
UPDATE tbl_modulo SET orden = 5 WHERE idmodulo = 25;
```

### Agregar nuevo submódulo:
```sql
INSERT INTO tbl_modulo (codigo, nombre, icono, url, orden, idmodulopadre, activo)
VALUES ('NUEVO_MOD', 'Nuevo Módulo', 'star', '/admin/nuevo', 4, 25, 1);

-- Dar permisos al rol Administrador
INSERT INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
VALUES (1, 1, LAST_INSERT_ID());
```

---

## 📂 Archivos creados:

1. ✅ `implementar_menu_dinamico.py` - Script para configurar la BD
2. ✅ `implementar_menu_dinamico.sql` - Queries SQL (alternativa manual)
3. ✅ `test_menu_dinamico.py` - Script para verificar la estructura
4. ✅ `analisis_menu_actual.md` - Análisis de tu estructura actual
5. ✅ Este archivo con instrucciones

---

## ❓ ¿Necesitas ayuda?

Si prefieres que te ayude a editar manualmente el archivo `base.html`, solo dime y lo hacemos paso a paso.

O si prefieres otra alternativa (sin usar `idmodulopadre`), también puedo implementarla.

¿Qué prefieres?
