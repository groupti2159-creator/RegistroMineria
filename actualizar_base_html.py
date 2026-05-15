"""
Script para actualizar base.html con el menú dinámico
"""

# Leer el archivo actual
with open('templates/base.html', 'r', encoding='utf-8') as f:
    contenido = f.read()

# Buscar el inicio del menú hardcodeado
inicio_marker = "{# ── DESVÍOS AMBIENTALES ── #}"
fin_marker = "{# ── MIS REPORTES (supervisor) ── #}"

# Encontrar las posiciones
inicio_pos = contenido.find(inicio_marker)
fin_pos = contenido.find(fin_marker)

if inicio_pos == -1 or fin_pos == -1:
    print("❌ No se encontraron los marcadores en el archivo")
    exit(1)

# Encontrar el final de la sección MIS_REPORTES
fin_seccion = contenido.find("{% endif %}", fin_pos)
if fin_seccion == -1:
    print("❌ No se encontró el cierre de MIS_REPORTES")
    exit(1)

# Avanzar hasta después del {% endif %}
fin_seccion += len("{% endif %}")

# Nuevo código dinámico
nuevo_codigo = """        {# ══════════════════════════════════════════════════════════════════════ #}
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
"""

# Construir el nuevo contenido
nuevo_contenido = (
    contenido[:inicio_pos] +
    nuevo_codigo +
    contenido[fin_seccion:]
)

# Guardar el archivo actualizado
with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(nuevo_contenido)

print("=" * 80)
print("✅ ARCHIVO base.html ACTUALIZADO EXITOSAMENTE")
print("=" * 80)
print("\n📝 Cambios realizados:")
print("   - Eliminado código hardcodeado de todos los módulos")
print("   - Implementado menú 100% dinámico desde base de datos")
print("\n🚀 Próximos pasos:")
print("   1. Reinicia la aplicación Flask")
print("   2. Cierra sesión y vuelve a iniciar sesión")
print("   3. ¡El menú ahora es completamente dinámico!")
print("\n💡 Para cambiar nombres:")
print("   UPDATE tbl_modulo SET nombre = 'Nuevo Nombre' WHERE idmodulo = 25;")
print("=" * 80)
