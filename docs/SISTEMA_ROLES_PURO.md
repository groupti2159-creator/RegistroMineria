# Sistema de Permisos por Roles (Opción A)

## 📋 Resumen

Sistema de gestión de permisos basado 100% en roles, siguiendo la propuesta del documento TablasAcces. Los permisos se asignan a roles, no a usuarios individuales.

## 🏗️ Arquitectura

```
┌─────────────┐
│  tbl_usuario│  ← Identidad (DNI, nombre, password)
└──────┬──────┘
       │
       ↓
┌─────────────────┐
│ tbl_usuariorol  │  ← Asignación (usuario + rol + proyecto + cargo)
└────────┬────────┘
         │
         ↓
┌──────────────────────────┐
│ tbl_proyecto_rol_modulo  │  ← Permisos (rol + proyecto + módulo)
└──────────────────────────┘
         │
         ↓
┌─────────────┐
│ tbl_modulo  │  ← Menús disponibles
└─────────────┘
```

## 📊 Tablas del Sistema

### 1. tbl_usuario (Identidad)
```sql
CREATE TABLE tbl_usuario (
    idusuario VARCHAR(8) PRIMARY KEY,  -- DNI
    nombrecompleto VARCHAR(100),
    correo VARCHAR(100),
    contrasena VARCHAR(255),
    activo TINYINT(1) DEFAULT 1
);
```

**Propósito**: Almacenar la identidad básica del usuario.

### 2. tbl_usuariorol (Asignación)
```sql
CREATE TABLE tbl_usuariorol (
    idusuariorol INT AUTO_INCREMENT PRIMARY KEY,
    idusuario VARCHAR(8),              -- FK a tbl_usuario
    idroles INT,                       -- FK a tbl_roles
    idproyecto INT,                    -- FK a tbl_proyecto
    idarea INT,                        -- FK a tbl_area
    cargo VARCHAR(100),
    FOREIGN KEY (idusuario) REFERENCES tbl_usuario(idusuario),
    FOREIGN KEY (idroles) REFERENCES tbl_roles(idroles),
    FOREIGN KEY (idproyecto) REFERENCES tbl_proyecto(idproyecto),
    FOREIGN KEY (idarea) REFERENCES tbl_area(idarea)
);
```

**Propósito**: Define QUÉ ROL tiene un usuario en QUÉ PROYECTO.

**Características**:
- Un usuario puede tener múltiples roles en diferentes proyectos
- Un usuario puede tener múltiples roles en el MISMO proyecto
- El cargo es descriptivo (no afecta permisos)

### 3. tbl_proyecto_rol_modulo (Permisos)
```sql
CREATE TABLE tbl_proyecto_rol_modulo (
    idproyectorolmodulo INT AUTO_INCREMENT PRIMARY KEY,
    idproyecto INT,                    -- FK a tbl_proyecto
    idroles INT,                       -- FK a tbl_roles
    idmodulo INT,                      -- FK a tbl_modulo
    FOREIGN KEY (idproyecto) REFERENCES tbl_proyecto(idproyecto),
    FOREIGN KEY (idroles) REFERENCES tbl_roles(idroles),
    FOREIGN KEY (idmodulo) REFERENCES tbl_modulo(idmodulo),
    UNIQUE KEY unique_permiso (idproyecto, idroles, idmodulo)
);
```

**Propósito**: Define QUÉ MÓDULOS puede ver cada ROL en cada PROYECTO.

**Nota**: Esta es la tabla "mágica" del documento TablasAcces (equivalente a `privilegio_rol_proyecto`).

### 4. tbl_modulo (Menús)
```sql
CREATE TABLE tbl_modulo (
    idmodulo INT AUTO_INCREMENT PRIMARY KEY,
    idproyecto INT,                    -- FK a tbl_proyecto
    idmodulopadre INT NULL,            -- FK a tbl_modulo (para jerarquía)
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(100),
    icono VARCHAR(50),
    url VARCHAR(200),
    orden INT DEFAULT 0,
    activo TINYINT(1) DEFAULT 1,
    FOREIGN KEY (idproyecto) REFERENCES tbl_proyecto(idproyecto),
    FOREIGN KEY (idmodulopadre) REFERENCES tbl_modulo(idmodulo)
);
```

**Propósito**: Catálogo de todos los menús/secciones disponibles en el sistema.

## 🔄 Flujo de Funcionamiento

### 1. Login del Usuario

```python
# 1. Usuario ingresa DNI y contraseña
dni = "12345678"
password = "******"

# 2. Validar credenciales
user = sp_login(dni, password)

# 3. Obtener roles del usuario
roles = SELECT * FROM tbl_usuariorol WHERE idusuario = dni

# 4. Si tiene múltiples roles, mostrar selector
if len(roles) > 1:
    # Usuario elige qué rol usar en esta sesión
    rol_elegido = roles[usuario_selecciona]
else:
    rol_elegido = roles[0]

# 5. Guardar en sesión
session['usuario_rol_id'] = rol_elegido.idusuariorol
session['rol_id'] = rol_elegido.idroles
session['proyecto_id'] = rol_elegido.idproyecto
```

### 2. Carga de Menú

```python
# Obtener módulos permitidos para el rol en el proyecto
modulos = SELECT m.* 
          FROM tbl_modulo m
          JOIN tbl_proyecto_rol_modulo prm 
            ON prm.idmodulo = m.idmodulo
          WHERE prm.idroles = session['rol_id']
            AND prm.idproyecto = session['proyecto_id']
            AND m.activo = 1
          ORDER BY m.orden

# Construir menú jerárquico
menu = construir_jerarquia(modulos)

# Renderizar en sidebar
render_menu(menu)
```

### 3. Verificación de Acceso

```python
@modulo_required('DESVIOS_AMB')
def dashboard():
    # Verificar que el usuario tenga acceso al módulo
    tiene_acceso = SELECT COUNT(*) 
                   FROM tbl_proyecto_rol_modulo prm
                   JOIN tbl_modulo m ON m.idmodulo = prm.idmodulo
                   WHERE prm.idroles = session['rol_id']
                     AND prm.idproyecto = session['proyecto_id']
                     AND m.codigo = 'DESVIOS_AMB'
    
    if not tiene_acceso:
        return redirect('/acceso-denegado')
    
    # Continuar con la lógica...
```

## 🎯 Gestión de Permisos (Pantalla de Admin)

### Interfaz de Configuración

El administrador configura permisos en 3 pasos:

1. **Seleccionar Proyecto**
   ```
   Proyecto: [Desvíos Ambientales ▼]
   ```

2. **Seleccionar Rol**
   ```
   Rol: [Supervisor ▼]
   ```

3. **Configurar Módulos**
   ```
   ☑ Dashboard
   ☑ Desvíos Ambientales
     ☑ Registrar Desvío
     ☑ Ver Reportes
     ☐ Configuración (deshabilitado)
   ☑ Gestión de Residuos
     ☑ Generación
     ☐ Comercializable (deshabilitado)
   ```

### Código de Guardado

```python
@admin_bp.route('/roles/guardar-permisos', methods=['POST'])
def guardar_permisos():
    proyecto_id = request.json['proyecto_id']
    rol_id = request.json['rol_id']
    modulos = request.json['modulos']  # Lista de IDs
    
    # 1. Eliminar permisos existentes
    DELETE FROM tbl_proyecto_rol_modulo
    WHERE idproyecto = proyecto_id AND idroles = rol_id
    
    # 2. Insertar nuevos permisos
    for modulo_id in modulos:
        INSERT INTO tbl_proyecto_rol_modulo 
        (idproyecto, idroles, idmodulo)
        VALUES (proyecto_id, rol_id, modulo_id)
    
    return {'success': True}
```

## 🔧 Casos de Uso

### Caso 1: Usuario con un solo rol

```
Usuario: Juan Pérez (DNI: 12345678)
Rol: Supervisor
Proyecto: Desvíos Ambientales

Módulos permitidos:
- Dashboard
- Desvíos Ambientales
  - Registrar Desvío
  - Ver Reportes
```

### Caso 2: Usuario con múltiples roles

```
Usuario: María García (DNI: 87654321)

Opción 1:
  Rol: Administrador
  Proyecto: Desvíos Ambientales
  Módulos: TODOS

Opción 2:
  Rol: Supervisor
  Proyecto: Gestión de Residuos
  Módulos: Dashboard, Gestión de Residuos
```

Al hacer login, María elige qué rol usar en esa sesión.

### Caso 3: Cambiar permisos de un rol

```
Antes:
  Rol: Trabajador
  Módulos: Dashboard, Mis Reportes

Cambio del Admin:
  Rol: Trabajador
  Módulos: Dashboard, Mis Reportes, Gestión de Residuos

Resultado:
  TODOS los usuarios con rol "Trabajador" ahora ven 
  "Gestión de Residuos" automáticamente
```

### Caso 4: Usuario necesita permisos especiales

```
Problema:
  Juan es Supervisor pero necesita acceso a Configuración

Solución INCORRECTA:
  ❌ Darle permisos personalizados a Juan

Solución CORRECTA:
  ✓ Crear rol "Supervisor Avanzado"
  ✓ Asignar módulos: Dashboard, Desvíos, Configuración
  ✓ Cambiar rol de Juan a "Supervisor Avanzado"
```

## ✅ Ventajas del Sistema

1. **Escalabilidad**: Gestionar 1000 usuarios = gestionar 5 roles
2. **Mantenibilidad**: Cambio en rol afecta a todos los usuarios
3. **Claridad**: Separación clara entre identidad, contexto y permisos
4. **Seguridad**: Menos puntos de falla, más fácil de auditar
5. **Simplicidad**: Una sola fuente de verdad para permisos

## ⚠️ Consideraciones Importantes

1. **Rol Administrador**: Debe tener acceso a TODOS los módulos
2. **Múltiples Roles**: Un usuario puede tener varios roles, pero usa UNO a la vez
3. **Cambio de Rol**: El usuario debe cerrar sesión y volver a entrar para cambiar de rol
4. **Nuevos Módulos**: Al agregar un módulo nuevo, configurar permisos para cada rol
5. **Eliminación de Roles**: Verificar que no haya usuarios asignados antes de eliminar

## 🚀 Migración desde Sistema Anterior

Ver archivo: `sql/migrar_a_sistema_roles_puro.sql`

Este script:
1. Migra permisos personalizados a permisos de rol
2. Crea backup de la tabla antigua
3. Elimina tabla obsoleta
4. Verifica integridad del sistema

## 📝 Próximos Pasos

1. ✅ Ejecutar script de migración
2. ✅ Actualizar `routes/auth.py`
3. ✅ Probar login con diferentes roles
4. ✅ Verificar que los menús se muestran correctamente
5. ✅ Probar pantalla de gestión de roles
6. ✅ Documentar para el equipo
