#!/usr/bin/env python3
"""
Script para actualizar las llamadas a Stored Procedures en el código Python
Convierte los nombres de SP de mayúsculas a minúsculas para Railway
"""

import os
import re

# Mapeo de stored procedures (mayúsculas -> minúsculas)
SP_MAPPING = {
    'SP_Login': 'sp_login',
    'SP_DashboardStats': 'sp_dashboardstats',
    'SP_ListarRegistros': 'sp_listarregistros',
    'SP_ListarRegistrosSupervisor': 'sp_listarregistrossupervisor',
    'SP_DetalleRegistro': 'sp_detalleregistro',
    'SP_ImagenesRegistro': 'sp_imagenesregistro',
    'SP_CrearRegistro': 'sp_crearregistro',
    'SP_ActualizarRegistro': 'sp_actualizarregistro',
    'SP_ArchivarRegistro': 'sp_archivarregistro',
    'SP_HistorialAdmin': 'sp_historialadmin',
    'SP_HistorialSupervisor': 'sp_historialsupervisor',
    'SP_Notificaciones': 'sp_notificaciones',
    'SP_ContarNotificaciones': 'sp_contarnotificaciones',
    'SP_CrearNotificacion': 'sp_crearnotificacion',
    'SP_LeerNotificacion': 'sp_leernotificacion',
    'SP_CambiarEstado': 'sp_cambiarestado',
    'SP_GuardarImagen': 'sp_guardarimagen',
    'SP_ValidarImagen': 'sp_validarimagen',
    'SP_EliminarImagen': 'sp_eliminarimagen',
    'SP_SiguienteCorrelativo': 'sp_siguientecorrelativo',
    'SP_ExportarRegistros': 'sp_exportarregistros',
}

def update_python_file(file_path):
    """Actualiza las llamadas a SP en un archivo Python"""
    print(f"Procesando: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = []
    
    # Buscar y reemplazar llamadas a stored procedures
    for old_sp, new_sp in SP_MAPPING.items():
        # Patrón para encontrar: sp_exec(cur, 'SP_Name', ...)
        pattern1 = rf"(sp_exec\s*\(\s*cur\s*,\s*['\"]){old_sp}(['\"])"
        if re.search(pattern1, content):
            content = re.sub(pattern1, rf"\1{new_sp}\2", content)
            changes.append(f"  sp_exec(..., '{old_sp}', ...) -> sp_exec(..., '{new_sp}', ...)")
        
        # Patrón para encontrar: sp_one(cur, 'SP_Name', ...)
        pattern2 = rf"(sp_one\s*\(\s*cur\s*,\s*['\"]){old_sp}(['\"])"
        if re.search(pattern2, content):
            content = re.sub(pattern2, rf"\1{new_sp}\2", content)
            changes.append(f"  sp_one(..., '{old_sp}', ...) -> sp_one(..., '{new_sp}', ...)")
    
    if content != original_content:
        # Guardar cambios
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Actualizado ({len(changes)} cambios)")
        for change in changes:
            print(change)
        return True
    else:
        print(f"  - Sin cambios necesarios")
        return False

def main():
    """Función principal"""
    print("=" * 70)
    print("Actualización de llamadas a Stored Procedures (mayúsculas -> minúsculas)")
    print("=" * 70)
    print()
    
    # Archivos Python a actualizar
    routes_dir = os.path.join(os.path.dirname(__file__), 'routes')
    python_files = [
        os.path.join(routes_dir, 'auth.py'),
        os.path.join(routes_dir, 'admin.py'),
        os.path.join(routes_dir, 'supervisor.py'),
        os.path.join(routes_dir, 'shared.py'),
    ]
    
    updated_count = 0
    
    for py_file in python_files:
        if os.path.exists(py_file):
            if update_python_file(py_file):
                updated_count += 1
        else:
            print(f"⚠ Archivo no encontrado: {py_file}")
    
    print()
    print("=" * 70)
    print(f"Actualización completada: {updated_count} archivos modificados")
    print("=" * 70)
    print()
    print("IMPORTANTE:")
    print("1. Los archivos Python fueron modificados directamente")
    print("2. Ahora las llamadas usan nombres en minúsculas")
    print("3. La funcionalidad NO cambió, solo los nombres de SP")
    print("4. Asegúrate de que la base de datos tenga los SP en minúsculas")
    print()

if __name__ == '__main__':
    main()
