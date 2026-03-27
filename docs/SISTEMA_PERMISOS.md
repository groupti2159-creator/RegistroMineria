# Sistema de Permisos y Accesos

## Estructura Actual

### Tablas Principales

#### 1. `tbl_proyecto`
Define los proyectos del sistema.
```
- idproyecto (PK)
- codigo (ej: DESVIOS_AMB, PRY001)
- nombre
- descripcion
- activo
```

#### 2. `tbl_roles`
Define los roles disponibles.
```
- idroles (PK)
- nombrerol (ej: Administrador, Supervisor, Trabajador)
- descripcion
```

#### 3. `tbl_modulo`
Define los módulos/menús del sistema.
```
- idmodulo (PK)
- idModuloPadre (para jerarquía)
- codigo (ej: CONFIG_USUARIOS, DATA_METRO_DASH)
- nombre
- icono
- url
- orden
- idproyecto (FK) ← Cada módulo pertenece a un proyecto
- activo
```

#### 4. `tbl_usuariorol`
Asigna usuarios a proyectos con un rol específico.
```
- idusuariorol (PK)
- idusuario (FK)
- idproyecto (FK)
- idroles (FK)
- idarea (FK, opcional)
- cargo (opcional)
```

### Sistema de Permisos (NUEVO - Recomendado)

#### 5. `tbl_proyecto_rol_modulo`
**Permisos base por rol en cada proyecto.**
Define qué módulos puede ver cada rol en cada proyecto.

```
- idproyectorolmodulo (PK)
- idproyecto (FK)
- idroles (FK)
- idmodulo (FK)
```

**Ejemplo:**
- Proyecto "Desvíos Ambientales" + Rol "Administrador" → Módulos [1,2,3,4,16,17,18]
- Proyecto "Inventario" + Rol "Supervisor" → Módulos [5,6,7]

#### 6. `tbl_usuario_modulo_personalizado`
**Permisos personalizados por usuario.**
Permite asignar módulos específicos a un usuario, sobrescribiendo los permisos del rol.

```
- idUsuarioModuloPersonalizado (PK)
- IdUsuarioRol (FK) ← Referencia a tbl_usuariorol
- idModulo (FK)
- Permitido (1=sí, 0=no)
- FechaAsignacion
```

**Ejemplo:**
- Usuario con idusuariorol=4 tiene módulos personalizados [1,2,3,4,16,17,18]

### Sistema de Permisos (ANTIGUO - Deprecado)

#### 7. `tbl_modulo_permiso` ⚠️ DEPRECADO
Sistema antiguo que no considera proyectos.

```
- idpermiso (PK)
- idmodulo (FK)
- idroles (FK)
- idarea (FK, opcional)
```

**Problema:** No soporta múltiples proyectos. Debe migrarse a `tbl_proyecto_rol_modulo`.

---

## Flujo de Autenticación y Permisos

### 1. Login
```python
# routes/auth.py → login()
1. Usuario ingresa DNI y contraseña
2. Se valida con sp_login
3. Se obtienen todas las asignaciones del usuario (tbl_usuariorol)
4. Si tiene múltiples roles → seleccionar_rol()
5. Si tiene un solo rol → set_session()
```

### 2. Cargar Módulos en Sesión
```python
# routes/auth.py → set_session()
1. Llamar a cargar_modulos(usuario_rol_id)
2. Si tiene módulos personalizados → usar esos
3. Si NO tiene módulos personalizados → usar cargar_accesos(rol_id) como fallback
```

### 3. Obtener Módulos Personalizados
```python
# routes/auth.py → cargar_modulos()
1. Llamar al SP: sp_obtenermodulospersonalizados(usuario_rol_id)
2. El SP consulta tbl_usuario_modulo_personalizado
3. Retorna módulos con jerarquía (padres e hijos)
4. Se construye el menú lateral
```

### 4. Fallback: Permisos del Rol
```python
# routes/auth.py → cargar_accesos()
⚠️ PROBLEMA: Usa tbl_modulo_permiso (sistema antiguo)
✅ SOLUCIÓN: Debe usar tbl_proyecto_rol_modulo
```

---

## Problemas Identificados

### ❌ Problema 1: Tabla `tbl_rolmodulo` no existe
**Error:** Consultas SQL buscan `tbl_rolmodulo` pero la tabla correcta es `tbl_proyecto_rol_modulo`.

**Archivos afectados:**
- `sql/diagnostico_usuario_nuevo.sql` (línea 46) ✅ CORREGIDO

### ❌ Problema 2: Stored Procedure con nombre incorrecto
**Error:** El código llama a `sp_obtenermodulospersonalizados` (minúsculas) pero el SP puede estar definido con otro nombre.

**Solución:** Crear/actualizar el SP con el nombre correcto.
- Script: `sql/fix_sp_modulos_personalizados.sql` ✅ CREADO

### ❌ Problema 3: Fallback usa sistema antiguo
**Error:** La función `cargar_accesos()` usa `tbl_modulo_permiso` en lugar de `tbl_proyecto_rol_modulo`.

**Impacto:** Usuarios sin módulos personalizados no ven nada o ven módulos incorrectos.

**Solución:** Actualizar `cargar_accesos()` para usar el sistema nuevo.

### ❌ Problema 4: Dos sistemas de permisos coexistiendo
**Error:** `tbl_modulo_permiso` (antiguo) y `tbl_proyecto_rol_modulo` (nuevo) están activos simultáneamente.

**Solución:** Migrar todos los permisos al sistema nuevo y deprecar `tbl_modulo_permiso`.

---

## Soluciones Implementadas

### ✅ 1. Script de Corrección del SP
**Archivo:** `sql/fix_sp_modulos_personalizados.sql`

Crea el stored procedure `sp_obtenermodulospersonalizados` con el nombre correcto.

### ✅ 2. Script de Prueba Completa
**Archivo:** `sql/test_usuario_completo.sql`

Permite verificar:
- Datos del usuario
- Asignaciones de rol y proyecto
- Módulos personalizados
- Módulos del rol (heredados)
- Resultado del stored procedure

### ✅ 3. Corrección de Diagnóstico
**Archivo:** `sql/diagnostico_usuario_nuevo.sql`

Actualizado para usar `tbl_proyecto_rol_modulo` en lugar de `tbl_rolmodulo`.

---

## Próximos Pasos

### 🔧 Paso 1: Ejecutar Scripts SQL
```bash
# 1. Corregir el stored procedure
mysql -u usuario -p desvios_ambientales < sql/fix_sp_modulos_personalizados.sql

# 2. Probar con un usuario específico
# Editar sql/test_usuario_completo.sql y cambiar @dni = '12345678'
mysql -u usuario -p desvios_ambientales < sql/test_usuario_completo.sql
```

### 🔧 Paso 2: Actualizar Función de Fallback
Modificar `routes/auth.py → cargar_accesos()` para usar `tbl_proyecto_rol_modulo`.

### 🔧 Paso 3: Migrar Permisos Antiguos
Crear script para migrar datos de `tbl_modulo_permiso` a `tbl_proyecto_rol_modulo`.

### 🔧 Paso 4: Deprecar Sistema Antiguo
Una vez migrado todo, eliminar referencias a `tbl_modulo_permiso`.

---

## Recomendaciones

1. **Usar siempre módulos personalizados:** Asignar módulos específicos a cada usuario al crearlo.
2. **Configurar permisos base por rol:** Definir en `tbl_proyecto_rol_modulo` qué ve cada rol por defecto.
3. **Eliminar sistema antiguo:** Una vez migrado, deprecar `tbl_modulo_permiso`.
4. **Documentar códigos de módulos:** Mantener lista actualizada de códigos (CONFIG_USUARIOS, DATA_METRO_DASH, etc.).

---

## Estructura Recomendada Final

```
Usuario
  └─ tbl_usuariorol (asignación a proyecto + rol)
       ├─ Opción A: Módulos Personalizados
       │    └─ tbl_usuario_modulo_personalizado
       │         └─ Lista específica de módulos
       │
       └─ Opción B: Permisos del Rol (fallback)
            └─ tbl_proyecto_rol_modulo
                 └─ Módulos base del rol en ese proyecto
```

**Prioridad:** Personalizados > Rol > Sin acceso
