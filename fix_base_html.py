"""
Script mejorado para actualizar base.html con menú dinámico
"""
import re

# Leer archivo
with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Patrón para encontrar todo el código hardcodeado del menú
# Desde "DESVÍOS AMBIENTALES" hasta antes de "</nav>"
pattern = r'{# ── DESVÍOS AMBIENTALES ── #}.*?{# ── MIS REPORTES \(supervisor\) ── #}.*?{% endif %}'

# Código dinámico de reemplazo
replacement = '''{# ══════════════════════════════════════════════════════════════════════ #}
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
        {% endfor %}'''

# Hacer el reemplazo usando regex con DOTALL para que . incluya saltos de línea
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Verificar que se hizo el cambio
if new_content == content:
    print("❌ ERROR: No se encontró el patrón para reemplazar")
    print("El archivo puede ya estar actualizado o tener un formato diferente")
else:
    # Guardar
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("=" * 80)
    print("✅ ARCHIVO base.html ACTUALIZADO CORRECTAMENTE")
    print("=" * 80)
    print("\n📝 Cambios:")
    print("   - Código hardcodeado eliminado")
    print("   - Menú 100% dinámico implementado")
    print("\n🚀 Siguiente paso:")
    print("   Reinicia Flask y vuelve a iniciar sesión")
    print("=" * 80)
