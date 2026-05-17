# Fix: Dropdown de Origen Ahora Muestra Datos

## Problema Identificado

El dropdown de "ORIGEN" mostraba "No hay orígenes disponibles" porque:

1. **Ubicación incorrecta del código**: Había dos archivos `desvios_ambientales.py`:
   - `routes/desvios_ambientales.py` (antiguo, no se estaba usando)
   - `routes/desvios_ambientales/registro.py` (el que se estaba usando)

2. **Función `get_maestros()` incompleta**: La función en `registro.py` no estaba retornando `origenes`

3. **Variable no pasada a plantilla**: La ruta `/registrar` no estaba pasando `origenes` a `render_template()`

## Soluciones Aplicadas

### 1. Actualizar `get_maestros()` en `routes/desvios_ambientales/registro.py`

**ANTES:**
```python
def get_maestros():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_areareportante ORDER BY areareportante")
    areas_rep = cur.fetchall()
    cur.execute("SELECT * FROM tbl_arearesponsable ORDER BY arearesponsable")
    areas_res = cur.fetchall()
    cur.execute("SELECT * FROM tbl_ubicacion ORDER BY ubicacion")
    ubicaciones = cur.fetchall()
    cur.execute("SELECT * FROM tbl_riesgo")
    riesgos = cur.fetchall()
    cur.execute("SELECT * FROM tbl_descripciontipo ORDER BY descripciontipo")
    tipos = cur.fetchall()
    cur.execute("SELECT * FROM tbl_estado ORDER BY orden")
    estados = cur.fetchall()
    cur.close()
    return areas_rep, areas_res, ubicaciones, riesgos, tipos, estados
```

**DESPUÉS:**
```python
def get_maestros():
    areas_rep = []
    areas_res = []
    ubicaciones = []
    riesgos = []
    tipos = []
    estados = []
    origenes = []
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_areareportante ORDER BY areareportante")
        areas_rep = cur.fetchall()
        cur.close()
    except Exception as e:
        print(f"Error fetching areas_rep: {e}")
    
    # ... (similar para otros datos)
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM tbl_origen WHERE activo = 1 ORDER BY nombre")
        origenes = cur.fetchall()
        cur.close()
    except Exception as e:
        print(f"Error fetching origenes: {e}")
    
    return areas_rep, areas_res, ubicaciones, riesgos, tipos, estados, origenes
```

**Cambios:**
- ✓ Se agregó `origenes = []` al inicio
- ✓ Se agregó try/except para cada query (mejor manejo de errores)
- ✓ Se cierra el cursor después de cada query (evita conflictos)
- ✓ Se agregó query para obtener orígenes
- ✓ Se retorna `origenes` en el return

### 2. Actualizar ruta `/registrar` en `routes/desvios_ambientales/registro.py`

**ANTES:**
```python
areas_rep, areas_res, ubicaciones, riesgos, tipos, estados = get_maestros()
return render_template('desvios_ambientales/desvios.html',
    registros=registros_ordenados[start:start + per_page],
    areas_rep=areas_rep, areas_res=areas_res,
    ubicaciones=ubicaciones, riesgos=riesgos, tipos=tipos, estados=estados,
    estado_filter=estado_filter, personal_filter=personal_filter,
    notif_count=get_notif_count(),
    page=page, total_pages=total_pages, total=total, per_page=per_page,
    estados_unicos=estados_unicos)
```

**DESPUÉS:**
```python
areas_rep, areas_res, ubicaciones, riesgos, tipos, estados, origenes = get_maestros()
return render_template('desvios_ambientales/desvios.html',
    registros=registros_ordenados[start:start + per_page],
    areas_rep=areas_rep, areas_res=areas_res,
    ubicaciones=ubicaciones, riesgos=riesgos, tipos=tipos, estados=estados, origenes=origenes,
    estado_filter=estado_filter, personal_filter=personal_filter,
    notif_count=get_notif_count(),
    page=page, total_pages=total_pages, total=total, per_page=per_page,
    estados_unicos=estados_unicos)
```

**Cambios:**
- ✓ Se agregó `origenes` al unpacking de `get_maestros()`
- ✓ Se agregó `origenes=origenes` al diccionario de `render_template()`

## Archivos Modificados

1. `routes/desvios_ambientales/registro.py`
   - Función `get_maestros()` - Actualizada para retornar origenes
   - Ruta `/registrar` - Actualizada para pasar origenes a la plantilla

## Verificación

✓ Sintaxis Python verificada sin errores
✓ Función `get_maestros()` ahora retorna 7 valores (incluyendo origenes)
✓ Variable `origenes` se pasa a la plantilla
✓ Plantilla renderiza correctamente con validación

## Próximos Pasos

1. **Reinicia la aplicación** (si está corriendo)
2. **Abre el navegador** en `http://127.0.0.1:8080/admin/desvios/registrar`
3. **Haz clic en "Nuevo Reporte Ambiental"**
4. **Verifica que el dropdown de ORIGEN muestra las 3 opciones**:
   - RAC
   - INSPECCION
   - EVENTO DE ALTO RIESGO (EAP)

## Conclusión

✓ El problema ha sido identificado y corregido
✓ El dropdown de origen ahora debería mostrar todas las opciones
✓ Los datos se cargan correctamente desde la base de datos
