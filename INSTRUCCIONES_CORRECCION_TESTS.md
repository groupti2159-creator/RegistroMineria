# Instrucciones para Corregir los Tests Fallidos

## Resumen
Actualmente hay 2 tests fallando de 35 totales (94% de éxito):
1. `test_tabla_ana_carga` - No hay datos en la tabla ANA
2. `test_editar_registro_efluente` - Modal no se abre correctamente

## 1. Insertar Datos de Prueba en Reporte ANA

### Paso 1: Ejecutar el script SQL
Abre Railway Workbench (o tu cliente MySQL) y ejecuta el archivo:
```
sql/insert_test_data_ana.sql
```

Este script insertará 10 registros de prueba en la tabla `tbl_registroana` con datos de Enero, Febrero y Marzo 2026.

### Verificación
Después de ejecutar el script, verifica que los datos se insertaron correctamente:
```sql
SELECT COUNT(*) FROM tbl_registroana;
-- Debería mostrar al menos 10 registros
```

## 2. Verificar que los Cambios en JavaScript se Aplicaron

### Archivos modificados:
1. `static/js/gestion_aguas/monitoreo.js` - Función `editarRegistro` ahora usa `abrirModal()` global
2. `static/js/gestion_aguas/reporte_ana.js` - Función `editarRegistro` usa `abrirModal()` global
3. `static/js/compromisos/registro.js` - Funciones de modal usan clase `.open`
4. `static/js/main.js` - Ya tiene las funciones globales `abrirModal()` y `cerrarModal()`

### Paso 2: Limpiar caché del navegador
1. Abre el navegador
2. Presiona `Ctrl + Shift + Delete`
3. Selecciona "Imágenes y archivos en caché"
4. Haz clic en "Borrar datos"

O simplemente recarga con `Ctrl + F5` en cada página.

## 3. Reiniciar el Servidor Flask

```bash
# Detener el servidor actual (Ctrl+C)
# Luego reiniciar:
python app.py
```

## 4. Ejecutar los Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# O ejecutar solo los tests que estaban fallando:
pytest tests/test_gestion_aguas.py::TestReporteANA::test_tabla_ana_carga -v
pytest tests/test_gestion_aguas.py::TestEfluentesCRUD::test_editar_registro_efluente -v
```

## 5. Verificación Manual

### Para Reporte ANA:
1. Abre http://127.0.0.1:8080/admin/ana
2. Deberías ver los 10 registros insertados
3. Haz clic en "Nuevo Reporte" - el modal debería abrirse con animación
4. Haz clic en el botón de editar de un registro - el modal debería abrirse con los datos

### Para Gestión de Aguas (Efluentes):
1. Abre http://127.0.0.1:8080/admin/aguas
2. Asegúrate de que hay al menos un registro de efluente
3. Haz clic en el botón de editar (ícono de lápiz)
4. El modal debería abrirse con animación mostrando los datos del registro

### Para Compromisos:
1. Abre http://127.0.0.1:8080/admin/compromisos
2. Haz clic en el botón de editar de cualquier compromiso
3. El modal debería abrirse con animación
4. Verifica que puedes ver evidencias (si hay alguna cargada)

## 6. Problemas Comunes y Soluciones

### Si el modal sigue sin aparecer:
1. Abre la consola del navegador (F12)
2. Ve a la pestaña "Console"
3. Busca errores en rojo
4. Si ves errores de "abrirModal is not defined", verifica que `main.js` se está cargando antes que los otros scripts

### Si los tests siguen fallando:
1. Verifica que el servidor Flask esté corriendo
2. Verifica que la base de datos tenga los datos insertados
3. Ejecuta los tests con más detalle:
   ```bash
   pytest tests/test_gestion_aguas.py::TestEfluentesCRUD::test_editar_registro_efluente -v -s
   ```
4. Revisa el output para ver exactamente dónde falla

## 7. Cambios Realizados en el Código

### CSS:
- Reorganizados en subcarpetas por módulo
- `base.css` contiene estilos globales de modales con clase `.open`
- Los modales ahora usan `opacity: 0` por defecto y `opacity: 1` con clase `.open`

### JavaScript:
- Todas las funciones que abren modales ahora agregan la clase `.open`
- Todas las funciones que cierran modales ahora remueven la clase `.open`
- Se usa la función global `abrirModal(id)` y `cerrarModal(id)` de `main.js`

### Tests:
- Función `_modal_abierto()` ahora verifica tanto `display !== 'none'` como `opacity !== '0'`
- Test de editar efluente ahora espera hasta 5 segundos para que el modal se abra

## 8. Resultado Esperado

Después de seguir estos pasos, deberías tener:
- ✅ 35/35 tests pasando (100%)
- ✅ Todos los modales funcionando correctamente con animaciones
- ✅ Datos de prueba en la tabla ANA
- ✅ Estructura de CSS organizada por módulos

## Contacto
Si después de seguir estos pasos aún hay problemas, revisa:
1. Los logs del servidor Flask
2. La consola del navegador
3. Que todos los archivos se guardaron correctamente
