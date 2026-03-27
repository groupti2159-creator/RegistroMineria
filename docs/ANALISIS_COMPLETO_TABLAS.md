# Análisis Completo de Tablas - Sistema de Permisos

## 📊 Estado Actual de las Tablas

### ✅ TABLAS QUE SE MANTIENEN (Correctas según TablasAcces)

#### 1. `tbl_usuario` - Identidad ✅
```sql
CREATE TABLE tbl_usuario (
    idusuario VARCHAR(20) PRIMARY KEY,      -- DNI
    nombrecompleto VARCHAR(100),
    correo VARCHAR(100),
    contrasena VARCHAR(255),
    activo TINYINT(1),
    fechacreacion DATETIME
);
```
**Estado**: ✅ PERFECTA - Cumple con el modelo del documento
**Acción**: MANTENER sin cambios

---

#### 2. `tbl_usuariorol` - Asignación ✅
```sql
CREATE TABLE tbl_usuariorol (
    idusuariorol INT AUTO_INCREMENT PRIMARY KEY,
    idusuario VARCHAR(20),                  -- FK a tbl_usuario (DNI)
    idroles INT,                            -- FK a tbl_roles
    idproyecto INT,                         -- FK a tbl_proyecto
    fechaasignacion DATETIME,
    idarea INT,                             -- FK a tbl_area
    cargo VARCHAR(100)
);
```
**Estado**: ✅ PERFECTA - Es exactamente la tabla "rol_usuariorol" del documento
**Acción**: MANTENER sin cambios
**Nota**: Esta tabla permite que un usuario tenga múltiples roles en múltiples proyectos

---

#### 3. `tbl_roles` - Catálogo de Roles ✅
```sql
CREATE TABLE tbl_roles (
    idroles INT AUTO_INCREMENT PRIMARY KEY,
    nombrerol VARCHAR(50),
    descripcion VARCHAR(200)
);
```
**Estado**: ✅ CORRECTA
**Acción**: MANTENER sin cambios
**Roles actuales**:
- 1: Administrador
- 2: Supervisor
- 3: Trabajador
- 5: Automatizador

---

#### 4. `tbl_proyecto` - Catálogo de Proyectos ✅
```sql
CREATE TABLE tbl_proyecto (
    idproyecto INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30),
    nombre VARCHAR(100),
    descripcion VARCHAR(300),
    activo TINYINT(1),
    fechacreacion DATETIME
);
```
**Estado**: ✅ CORRECTA
**Acción**: MANTENER sin cambios

---

#### 5. `tbl_modulo` - Catálogo de Menús ✅
```sql
CREATE TABLE tbl_modulo (
    idmodulo INT AUTO_INCREMENT PRIMARY KEY,
    idModuloPadre INT,                      -- Para jerarquía de menús
    codigo VARCHAR(30),
    nombre VARCHAR(100),
    icono VARCHAR(50),
    url VARCHAR(200),
    orden INT,
    idproyecto INT,                         -- FK a tbl_proyecto
    activo TINYINT(1)
);
```
**Estado**: ✅ CORRECTA - Soporta jerarquía de menús
**Acción**: MANTENER sin cambios
**Nota**: Tiene 36 módulos configurados para el proyecto "Desvíos Ambientales"

---

### ❌ TABLAS QUE SE ELIMINAN (Obsoletas)

#### 6. `tbl_usuario_modulo_personalizado` - Permisos Personalizados ❌
```sql
CREATE TABLE tbl_usuario_modulo_personalizado (
    idUsuarioModuloPersonalizado INT AUTO_INCREMENT PRIMARY KEY,
    IdUsuarioRol INT,
    idModulo INT,
    Permitido TINYINT(1),
    FechaAsignacion DATETIME
);
```
**Estado**: ❌ OBSOLETA - Va contra el modelo de roles puro
**Problema**: Permite permisos individuales por usuario, lo que complica la gestión
**Acción**: ELIMINAR después de migrar datos
**Datos actuales**: 3 registros (usuario_rol_id=4 tiene 3 módulos personalizados)

---

#### 7. `tbl_modulo_permiso` - Permisos Antiguos ❌
```sql
CREATE TABLE tbl_modulo_permiso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    idmodulo INT,
    idroles INT,
    idarea INT
);
```
**Estado**: ❌ OBSOLETA - No sigue el modelo correcto
**Problemas**:
- No tiene relación con `idproyecto` (un rol puede tener diferentes permisos en diferentes proyectos)
- Mezcla `idroles` con `idarea` (conceptos diferentes)
- Solo 5 registros, todos para rol Administrador
**Acción**: ELIMINAR (datos no son útiles)

---

### ➕ TABLA QUE FALTA (Necesaria según TablasAcces)

#### 8. `tbl_proyecto_rol_modulo` - Permisos por Rol ➕
```sql
-- ESTA TABLA DEBE EXISTIR O CREARSE
CREATE TABLE tbl_proyecto_rol_modulo (
    idproyectorolmodulo INT AUTO_INCREMENT PRIMARY KEY,
    idproyecto INT NOT NULL,                -- FK a tbl_proyecto
    idroles INT NOT NULL,                   -- FK a tbl_roles
    idmodulo INT NOT NULL,                  -- FK a tbl_modulo
    FOREIGN KEY (idproyecto) REFERENCES tbl_proyecto(idproyecto),
    FOREIGN KEY (idroles) REFERENCES tbl_roles(idroles),
    FOREIGN KEY (idmodulo) REFERENCES tbl_modulo(idmodulo),
    UNIQUE KEY unique_permiso (idproyecto, idroles, idmodulo)
);
```
**Estado**: ❓ VERIFICAR SI EXISTE
**Propósito**: Esta es la tabla "privilegio_rol_proyecto" del documento TablasAcces
**Acción**: 
- Si existe: MANTENER y verificar datos
- Si NO existe: CREAR

---

## 🔄 Plan de Migración

### Fase 1: Verificación
```sql
-- Verificar si existe tbl_proyecto_rol_modulo
SHOW TABLES LIKE 'tbl_proyecto_rol_modulo';

-- Si existe, ver su estructura
DESCRIBE tbl_proyecto_rol_modulo;

-- Ver cuántos registros tiene
SELECT COUNT(*) FROM tbl_proyecto_rol_modulo;
```

### Fase 2: Creación (si no existe)
```sql
CREATE TABLE tbl_proyecto_rol_modulo (
    idproyectorolmodulo INT AUTO_INCREMENT PRIMARY KEY,
    idproyecto INT NOT NULL,
    idroles INT NOT NULL,
    idmodulo INT NOT NULL,
    FOREIGN KEY (idproyecto) REFERENCES tbl_proyecto(idproyecto) ON DELETE CASCADE,
    FOREIGN KEY (idroles) REFERENCES tbl_roles(idroles) ON DELETE CASCADE,
    FOREIGN KEY (idmodulo) REFERENCES tbl_modulo(idmodulo) ON DELETE CASCADE,
    UNIQUE KEY unique_permiso (idproyecto, idroles, idmodulo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Fase 3: Migración de Datos

#### 3.1 Migrar desde tbl_usuario_modulo_personalizado
```sql
-- Identificar qué rol tiene el usuario_rol_id=4
SELECT ur.idroles, ur.idproyecto, ump.idmodulo
FROM tbl_usuario_modulo_personalizado ump
JOIN tbl_usuariorol ur ON ur.idusuariorol = ump.IdUsuarioRol
WHERE ump.Permitido = 1;

-- Insertar en tbl_proyecto_rol_modulo
INSERT INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
SELECT DISTINCT ur.idproyecto, ur.idroles, ump.idmodulo
FROM tbl_usuario_modulo_personalizado ump
JOIN tbl_usuariorol ur ON ur.idusuariorol = ump.IdUsuarioRol
WHERE ump.Permitido = 1
  AND NOT EXISTS (
      SELECT 1 FROM tbl_proyecto_rol_modulo prm
      WHERE prm.idproyecto = ur.idproyecto
        AND prm.idroles = ur.idroles
        AND prm.idmodulo = ump.idmodulo
  );
```

#### 3.2 Configurar permisos para Administrador
```sql
-- El Administrador debe tener acceso a TODOS los módulos
INSERT INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo)
SELECT DISTINCT m.idproyecto, 1 AS idroles, m.idmodulo
FROM tbl_modulo m
WHERE m.activo = 1
  AND NOT EXISTS (
      SELECT 1 FROM tbl_proyecto_rol_modulo prm
      WHERE prm.idproyecto = m.idproyecto
        AND prm.idroles = 1
        AND prm.idmodulo = m.idmodulo
  );
```

### Fase 4: Limpieza
```sql
-- Crear backups
CREATE TABLE tbl_usuario_modulo_personalizado_backup AS 
SELECT * FROM tbl_usuario_modulo_personalizado;

CREATE TABLE tbl_modulo_permiso_backup AS 
SELECT * FROM tbl_modulo_permiso;

-- Eliminar tablas obsoletas
DROP TABLE tbl_usuario_modulo_personalizado;
DROP TABLE tbl_modulo_permiso;
```

---

## 📋 Resumen de Acciones

### ✅ MANTENER (5 tablas)
1. `tbl_usuario` - Identidad de usuarios
2. `tbl_usuariorol` - Asignación de roles a usuarios
3. `tbl_roles` - Catálogo de roles
4. `tbl_proyecto` - Catálogo de proyectos
5. `tbl_modulo` - Catálogo de menús

### ➕ CREAR/VERIFICAR (1 tabla)
6. `tbl_proyecto_rol_modulo` - Permisos por rol (la tabla "mágica")

### ❌ ELIMINAR (2 tablas)
7. `tbl_usuario_modulo_personalizado` - Permisos personalizados (obsoleta)
8. `tbl_modulo_permiso` - Permisos antiguos (obsoleta)

---

## 🎯 Estructura Final del Sistema

```
┌─────────────┐
│ tbl_usuario │ ← Identidad (DNI, nombre, password)
└──────┬──────┘
       │
       ↓
┌──────────────────┐
│ tbl_usuariorol   │ ← Asignación (usuario + rol + proyecto + área + cargo)
└────────┬─────────┘
         │
         ↓
┌───────────────────────────┐
│ tbl_proyecto_rol_modulo   │ ← Permisos (proyecto + rol + módulo)
└─────────────┬─────────────┘
              │
              ↓
┌─────────────┐
│ tbl_modulo  │ ← Menús disponibles
└─────────────┘
```

---

## 🔍 Verificación de Datos Actuales

### Usuarios
- Total: 5 usuarios
- Todos activos

### Asignaciones (tbl_usuariorol)
- Total: 6 asignaciones
- Usuario 11111111: 2 roles (Administrador y Supervisor)
- Usuario 74185296: 2 roles (Administrador y Supervisor)
- Otros: 1 rol cada uno

### Módulos
- Total: 36 módulos
- Todos para proyecto "Desvíos Ambientales" (idproyecto=1)
- Todos activos

### Permisos Personalizados (a migrar)
- Usuario_rol_id=4 tiene 3 módulos personalizados
- Estos deben convertirse en permisos del rol correspondiente

---

## 📝 Próximos Pasos

1. ✅ Verificar si existe `tbl_proyecto_rol_modulo`
2. ➕ Crear `tbl_proyecto_rol_modulo` si no existe
3. 🔄 Migrar datos de tablas obsoletas
4. ❌ Eliminar tablas obsoletas (con backup)
5. ✅ Configurar permisos para todos los roles
6. 🧪 Probar el sistema completo
