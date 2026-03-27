# Análisis Completo: Tablas de Acceso y Creación de Usuarios

## Tablas Identificadas en el Sistema

### 1. **tbl_usuario** (Tabla Base)
**Propósito:** Almacenar información básica del usuario

**Estructura:**
```
- idusuario (PK) - DNI del usuario
- nombrecompleto
- correo
- contrasena (MD5)
- activo (1=activo, 0=inactivo)
```

**Uso:**
- Creación: `routes/admin.py → usuarios_crear_nuevo()`
- Login: `routes/auth.py → login()` (valida con sp_login)

---

### 2. **tbl_usuariorol** (EJE CENTRAL - Contexto del Usuario)
**Propósito:** Define el contexto funcional del usuario en el sistema

**Estructura:**
```
- idusuariorol (PK) - ID único de la asignación
- idusuario (FK) - Referencia a tbl_usuario
- idproyecto (FK) - Proyecto asignado
- idroles (FK) - Rol asignado
- idarea (FK) - Área responsable
- cargo - Cargo del usuario
- fechaasignacion - Fecha de creación
```

**Características:**
- Un usuario puede tener MÚLTIPLES asignaciones (múltiples proyectos/roles)
- Cada asignación genera un `idusuariorol` único
- Este ID es la clave para los permisos personalizados

**Uso:**
- Creación: `routes/admin.py → usuarios_crear_nuevo()` (INSERT)
- Login: `routes/auth.py → login()` (SELECT para obtener todas las asignaciones)
- Selección de rol: `routes/auth.py → seleccionar_rol()` (cuando hay múltiples)

**Ejemplo de datos:**
```
idusuariorol=4, idusuario='12345678', idproyecto=1, idroles=2, idarea=3, cargo='Supervisor'
idusuariorol=5, idusuario='12345678', idproyecto=4, idroles=3, idarea=2, cargo='Trabajador'
```

---

### 3. **tbl_usuario_modulo_personalizado** (Permisos Personalizados)
**Propósito:** Define qué módulos puede ver cada usuario específicamente

**Estructura:**
```
- idusuariomodulopersonalizado (PK)
- idusuariorol (FK) - Referencia a tbl_usuariorol ← CLAVE
- idmodulo (FK) - Módulo permitido
- permitido (1=sí, 0=no)
- fechaasignacion
```

**Características:**
- Vincula `idusuariorol` (no `idusuario`) con módulos
- Permite control granular por asignación
- Si un usuario tiene 2 proyectos, puede tener diferentes módulos en cada uno

**Uso:**
- Creación: `routes/admin.py → usuarios_crear_nuevo()` (INSERT múltiple)
- Login: `routes/auth.py → cargar_modulos()` (SELECT vía SP)

**Ejemplo de datos (según TablasAcces):**
```
idusuariorol=4 → módulos [1,2,3,4,16,17,18]
```

---

### 4. **tbl_modulo** (Catálogo de Módulos)
**Propósito:** Define todos los módulos/menús disponibles en el sistema

**Estructura:**
```
- idmodulo (PK)
- idmodulopadre (FK) - Para jerarquía (padre/hijo)
- codigo - Código único (ej: CONFIG_USUARIOS, DATA_METRO_DASH)
- nombre - Nombre visible
- icono - Icono del menú
- url - Ruta del módulo
- orden - Orden de visualización
- idproyecto (FK) - Proyecto al que pertenece
- activo (1=activo, 0=inactivo)
```

**Características:**
- Soporta jerarquía (módulos padre con hijos)
- Cada módulo pertenece a un proyecto
- Se usa para construir el menú lateral dinámicamente

**Ejemplo de datos (según TablasAcces):**
```
idmodulo=28, codigo='CONFIG_USUARIOS', nombre='Configuración de Usuarios', 
icono='users', url='/admin/configuracion/usuarios', orden=51, idproyecto=1
```

---

### 5. **tbl_proyecto** (Catálogo de Proyectos)
**Propósito:** Define los proyectos disponibles en el sistema

**Estructura:**
```
- idproyecto (PK)
- codigo - Código único (ej: DESVIOS_AMB, PRY001)
- nombre
- descripcion
- activo
- fechacreacion
```

**Ejemplo de datos (según TablasAcces):**
```
idproyecto=1, codigo='DESVIOS_AMB', nombre='Desvíos Ambientales'
idproyecto=4, codigo='PRY001', nombre='Sistema de Inventario'
```

---

### 6. **tbl_roles** (Catálogo de Roles)
**Propósito:** Define los roles disponibles (solo referencia)

**Estructura:**
```
- idroles (PK)
- nombrerol
- descripcion
```

**Ejemplo de datos (según TablasAcces):**
```
idroles=1, nombrerol='Administrador'
idroles=2, nombrerol='Supervisor'
idroles=3, nombrerol='Trabajador'
idroles=5, nombrerol='Automatizador'
```

**Nota:** En tu modelo, el rol es solo una etiqueta. Los permisos NO se heredan del rol.

---

### 7. **tbl_arearesponsable** (Catálogo de Áreas)
**Propósito:** Define las áreas de la organización

**Estructura:**
```
- idarearesponsable (PK)
- arearesponsable
```

**Uso:**
- Referencia en `tbl_usuariorol`
- Carga en formulario: `routes/admin.py → usuarios_form_data()`

---

## Tablas OBSOLETAS (No necesarias en tu modelo)

### ❌ **tbl_proyecto_rol_modulo**
**Por qué existe:** Sistema de permisos por rol (heredados)

**Estructura:**
```
- idproyectorolmodulo (PK)
- idproyecto (FK)
- idroles (FK)
- idmodulo (FK)
```

**Problema:** Tu modelo NO usa permisos heredados por rol. Cada usuario tiene permisos personalizados.

**Estado:** Existe en la BD pero NO se usa en tu flujo de creación de usuarios.

**Recomendación:** 
- Opción A: Eliminarla si no la necesitas
- Opción B: Usarla como "plantilla" para asignar módulos por defecto al crear usuario

---

### ❌ **tbl_modulo_permiso**
**Por qué existe:** Sistema antiguo de permisos

**Estructura:**
```
- idpermiso (PK)
- idmodulo (FK)
- idroles (FK)
- idarea (FK)
```

**Problema:** Sistema antiguo que no considera proyectos.

**Estado:** Existe en la BD y se usa como fallback en `cargar_accesos()`

**Recomendación:** Eliminar completamente. No encaja en tu modelo.

---

## Flujo Completo: Creación de Usuario

### Paso 1: Formulario de Creación
**Archivo:** `templates/configuracion/usuarios.html`
**JavaScript:** `static/js/admin/usuarios.js`

**Datos requeridos:**
- DNI
- Nombre completo
- Correo (opcional)
- Contraseña
- Asignaciones (array):
  - Proyecto
  - Rol
  - Área
  - Cargo
  - Módulos (array de IDs)

### Paso 2: Backend - Crear Usuario
**Ruta:** `POST /admin/usuarios/crear-nuevo`
**Archivo:** `routes/admin.py → usuarios_crear_nuevo()`

**Proceso:**
```python
1. INSERT INTO tbl_usuario (dni, nombre, correo, password)
2. Para cada asignación:
   a. INSERT INTO tbl_usuariorol (usuario, proyecto, rol, area, cargo)
   b. Obtener idusuariorol (LAST_INSERT_ID)
   c. Para cada módulo seleccionado:
      INSERT INTO tbl_usuario_modulo_personalizado (idusuariorol, idmodulo)
```

### Paso 3: Login del Usuario
**Ruta:** `POST /login`
**Archivo:** `routes/auth.py → login()`

**Proceso:**
```python
1. Validar DNI y contraseña (sp_login)
2. SELECT todas las asignaciones de tbl_usuariorol
3. Si tiene múltiples asignaciones → seleccionar_rol()
4. Si tiene una sola → set_session()
```

### Paso 4: Cargar Módulos en Sesión
**Función:** `routes/auth.py → set_session()`

**Proceso:**
```python
1. Llamar cargar_modulos(idusuariorol)
2. SP: sp_obtenermodulospersonalizados(idusuariorol)
3. SELECT módulos de tbl_usuario_modulo_personalizado
4. Construir jerarquía (padres e hijos)
5. Guardar en session['modulos']
```

---

## Análisis del Problema Actual

### ❌ Problema 1: Stored Procedure No Existe o Está Mal
**Error:** `sp_obtenermodulospersonalizados` retorna 0 filas

**Causa posible:**
- El SP no existe
- El SP tiene nombre diferente
- El SP usa tabla incorrecta

**Solución:** Ejecutar `sql/fix_sp_modulos_personalizados.sql`

### ❌ Problema 2: Fallback Innecesario
**Código:** `routes/auth.py → cargar_accesos()`

**Problema:** Si no hay módulos personalizados, intenta usar `tbl_modulo_permiso` o `tbl_proyecto_rol_modulo`

**Solución:** En tu modelo, NO debe haber fallback. Si un usuario no tiene módulos → error.

### ❌ Problema 3: Tablas Obsoletas Activas
**Problema:** `tbl_modulo_permiso` y `tbl_proyecto_rol_modulo` existen y se usan como fallback

**Solución:** Eliminar referencias en el código.

---

## Recomendaciones

### 1. Simplificar el Código
- Eliminar función `cargar_accesos()` (fallback innecesario)
- Eliminar referencias a `tbl_modulo_permiso`
- Eliminar referencias a `tbl_proyecto_rol_modulo` (o usarla como plantilla)

### 2. Validación Obligatoria
- Al crear usuario, DEBE asignar al menos un módulo
- Al hacer login, si no tiene módulos → mostrar error claro

### 3. Usar tbl_proyecto_rol_modulo como Plantilla (Opcional)
- Mantener la tabla para definir módulos "sugeridos" por rol
- Al crear usuario, pre-seleccionar módulos según el rol elegido
- El admin puede modificar antes de guardar

### 4. Ejecutar Scripts SQL
```bash
# 1. Crear/corregir el stored procedure
mysql -u root -p desvios_ambientales < sql/fix_sp_modulos_personalizados.sql

# 2. Probar con usuario existente
# Editar sql/test_usuario_completo.sql (cambiar @dni)
mysql -u root -p desvios_ambientales < sql/test_usuario_completo.sql
```

---

## Resumen: Tablas Necesarias vs Obsoletas

### ✅ NECESARIAS (Tu Modelo)
1. `tbl_usuario` - Datos básicos
2. `tbl_usuariorol` - Contexto (EJE CENTRAL)
3. `tbl_usuario_modulo_personalizado` - Permisos personalizados
4. `tbl_modulo` - Catálogo de módulos
5. `tbl_proyecto` - Catálogo de proyectos
6. `tbl_roles` - Catálogo de roles (solo referencia)
7. `tbl_arearesponsable` - Catálogo de áreas

### ❌ OBSOLETAS (No necesarias)
1. `tbl_modulo_permiso` - Sistema antiguo
2. `tbl_proyecto_rol_modulo` - Permisos por rol (no usas herencia)

### ⚠️ OPCIONAL
- Mantener `tbl_proyecto_rol_modulo` solo como "plantilla" para sugerir módulos al crear usuario
