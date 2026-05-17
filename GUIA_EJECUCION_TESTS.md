# Guía de Ejecución de Tests

## Descripción General

Este documento proporciona instrucciones para ejecutar los diferentes tipos de pruebas disponibles en el proyecto ecoSupervisor.

## Tests Disponibles

### 1. Test de Maestros (test_maestros.py)
Verifica que la función `get_maestros()` retorna todos los datos correctamente.

**Ejecución:**
```bash
python test_maestros.py
```

**Qué verifica:**
- Carga de áreas reportantes
- Carga de áreas responsables
- Carga de ubicaciones
- Carga de riesgos
- Carga de tipos de descripción
- Carga de estados
- **Carga de orígenes** ✓

**Salida esperada:**
```
areas_rep: 13
areas_res: 6
ubicaciones: 6
riesgos: 3
tipos: 2
estados: 9
origenes: 3

Detalles de origenes:
  - ID: 3, Nombre: EVENTO DE ALTO RIESGO (EAP)
  - ID: 2, Nombre: INSPECCION
  - ID: 1, Nombre: RAC
```

### 2. Test de Flujo Completo (test_full_flow.py)
Verifica el flujo completo de carga de la página de registros.

**Ejecución:**
```bash
python test_full_flow.py
```

**Qué verifica:**
- Importación correcta de módulos
- Carga de maestros
- Disponibilidad de orígenes

**Salida esperada:**
```
✓ origenes tiene 3 registros
✓ TEST COMPLETADO EXITOSAMENTE
```

### 3. Test Final (test_final.py)
Prueba básica de creación de proyectos.

**Ejecución:**
```bash
python test_final.py
```

**Qué verifica:**
- Importación de la aplicación
- Creación de cliente de prueba
- Manejo de redirects

**Salida esperada:**
```
✓ App importada
✓ Cliente creado
✓ Redirección recibida (esperado para POST sin sesión)
```

### 4. Test de Depuración Completo (run_all_tests.py) ⭐ RECOMENDADO
Script completo que ejecuta todos los tests de depuración.

**Ejecución:**
```bash
python run_all_tests.py
```

**Qué verifica:**
1. **Imports**: Verifica que todos los módulos se importan correctamente
2. **get_maestros()**: Verifica que retorna 7 valores correctamente
3. **Conexión BD**: Verifica que la conexión a MySQL funciona
4. **Estructura de archivos**: Verifica que todos los archivos requeridos existen

**Salida esperada:**
```
✓ PASÓ: Imports
✓ PASÓ: get_maestros()
✓ PASÓ: Conexión BD
✓ PASÓ: Estructura archivos

✓ TODOS LOS TESTS PASARON
```

### 5. Tests de Selenium (tests/test_desvios_ambientales.py)
Pruebas de interfaz de usuario usando Selenium.

**Requisitos previos:**
- Aplicación ejecutándose en http://127.0.0.1:8080
- ChromeDriver instalado (se descarga automáticamente)
- Credenciales de prueba configuradas en conftest.py

**Ejecución:**
```bash
# Ejecutar todos los tests de desvios
pytest tests/test_desvios_ambientales.py -v

# Ejecutar solo tests de humo (smoke tests)
pytest tests/test_desvios_ambientales.py -m smoke -v

# Ejecutar tests específicos
pytest tests/test_desvios_ambientales.py::TestDesviosSmoke::test_pagina_registrar_carga -v

# Generar reporte HTML
pytest tests/test_desvios_ambientales.py -v --html=tests/reporte.html --self-contained-html
```

**Clases de Tests Disponibles:**
- `TestDesviosSmoke`: Pruebas rápidas de carga
- `TestDesviosFiltros`: Pruebas de filtrado
- `TestDesviosModalCrear`: Pruebas del modal de creación
- `TestDesviosModalDetalle`: Pruebas del modal de detalle
- `TestDesviosModalEditar`: Pruebas del modal de edición
- `TestDesviosEliminar`: Pruebas de eliminación

## Configuración de Credenciales

Para ejecutar los tests de Selenium, edita `tests/conftest.py`:

```python
BASE_URL  = "http://127.0.0.1:8080"
DNI       = "12345678"    # Cambiar por DNI válido
PASSWORD  = "admin123"    # Cambiar por contraseña válida
HEADLESS  = False         # True para ejecutar sin interfaz gráfica
```

## Solución de Problemas

### Error: "ImportError: cannot import name 'get_maestros'"
**Solución**: Asegúrate de usar el import correcto:
```python
from routes.desvios_ambientales.registro import get_maestros
```

### Error: "Connection refused" en tests de Selenium
**Solución**: Asegúrate de que la aplicación está ejecutándose:
```bash
python app.py
```

### Error: "ChromeDriver not found"
**Solución**: Se descargará automáticamente. Si no funciona, instala manualmente:
```bash
pip install webdriver-manager
```

### Error: "No hay orígenes en la base de datos"
**Solución**: Verifica que la tabla `tbl_origen` tiene datos:
```sql
SELECT * FROM tbl_origen WHERE activo = 1;
```

## Flujo Recomendado de Pruebas

1. **Primero**: Ejecutar `run_all_tests.py` para verificar la configuración básica
2. **Luego**: Ejecutar `test_maestros.py` para verificar datos
3. **Después**: Ejecutar `test_full_flow.py` para verificar flujo
4. **Finalmente**: Ejecutar tests de Selenium para validar interfaz

## Generación de Reportes

Los tests de Selenium generan un reporte HTML automáticamente:

```bash
pytest tests/test_desvios_ambientales.py -v --html=tests/reporte.html --self-contained-html
```

El reporte se guardará en `tests/reporte.html` y puede abrirse en cualquier navegador.

## Notas Importantes

- Los tests de Selenium requieren que la aplicación esté ejecutándose
- Los tests de depuración (test_maestros.py, test_full_flow.py) no requieren la aplicación ejecutándose
- El campo `origen` está completamente implementado y funcional
- Todos los tests pasaron exitosamente

## Contacto y Soporte

Para reportar problemas o sugerencias, contacta al equipo de desarrollo.
