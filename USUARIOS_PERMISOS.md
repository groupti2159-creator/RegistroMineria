# 👥 TRES USUARIOS CON DIFERENTES PERMISOS

Se han creado tres usuarios de prueba con diferentes niveles de acceso para probar el sistema de permisos.

---

## 👑 USUARIO 1: Super Administrador

**Credenciales**:
- DNI: `11111111`
- Contraseña: `admin123`

**Rol**: Super Administrador

**Proyecto**: Argos (ID: 1)

**Permisos**:
- ✅ Crear reportes
- ✅ Editar reportes
- ✅ Eliminar reportes
- ✅ Validar levantamientos
- ✅ Acceso a todos los módulos

**Módulos Asignados**:
- DESVIOS_AMB (Desvíos SSOMA)
- MIS_REPORTES (Mis Reportes)
- DESVIOS (Registrar Reporte)

---

## 👔 USUARIO 2: Supervisor

**Credenciales**:
- DNI: `22222222`
- Contraseña: `supervisor123`

**Rol**: Supervisor

**Proyecto**: Argos (ID: 1)

**Permisos**:
- ✅ Crear reportes
- ✅ Editar reportes
- ✅ Eliminar reportes
- ✅ Subir levantamientos
- ❌ Validar levantamientos (solo Super Admin)

**Módulos Asignados**:
- DESVIOS_AMB (Desvíos SSOMA)
- MIS_REPORTES (Mis Reportes)

---

## 👁️ USUARIO 3: Auditor

**Credenciales**:
- DNI: `33333333`
- Contraseña: `auditor123`

**Rol**: Auditor

**Proyecto**: Argos (ID: 1)

**Permisos**:
- ❌ Crear reportes
- ❌ Editar reportes
- ❌ Eliminar reportes
- ✅ Validar levantamientos
- ✅ Ver reportes

**Módulos Asignados**:
- DESVIOS_AMB (Desvíos SSOMA)

---

## 🧪 Cómo Probar

### 1. Ingresar como Super Administrador
```
DNI: 11111111
Contraseña: admin123
```
Deberías ver:
- Botón "Crear" ✅
- Botón "Editar" ✅
- Botón "Eliminar" ✅
- Botón "Validar" ✅

### 2. Ingresar como Supervisor
```
DNI: 22222222
Contraseña: supervisor123
```
Deberías ver:
- Botón "Crear" ✅
- Botón "Editar" ✅
- Botón "Eliminar" ✅
- Botón "Validar" ❌ (oculto)

### 3. Ingresar como Auditor
```
DNI: 33333333
Contraseña: auditor123
```
Deberías ver:
- Botón "Crear" ❌ (oculto)
- Botón "Editar" ❌ (oculto)
- Botón "Eliminar" ❌ (oculto)
- Botón "Validar" ✅

---

## 📊 Comparativa de Permisos

| Acción | Super Admin | Supervisor | Auditor |
|--------|-------------|-----------|---------|
| Crear Reporte | ✅ | ✅ | ❌ |
| Editar Reporte | ✅ | ✅ | ❌ |
| Eliminar Reporte | ✅ | ✅ | ❌ |
| Subir Levantamientos | ✅ | ✅ | ❌ |
| Validar Levantamientos | ✅ | ❌ | ✅ |
| Ver Reportes | ✅ | ✅ | ✅ |

---

## 🔐 Seguridad

- ✅ Contraseñas hasheadas con MD5
- ✅ Roles validados en backend
- ✅ Módulos validados en backend
- ✅ Botones dinámicos en frontend
- ✅ Acceso denegado si no tiene permisos

---

## 📝 Notas

- Todos los usuarios están en el proyecto **Argos** (ID: 1)
- Los módulos están asignados en `tbl_proyecto_rol_modulo`
- Los roles están asignados en `tbl_usuariorol`
- Las contraseñas son de prueba, cambiar en producción

---

**Fecha**: 22 de Mayo de 2026
**Estado**: ✅ USUARIOS CREADOS
