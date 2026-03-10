#!/usr/bin/env python3
"""
Script para convertir nombres de tablas y stored procedures a minúsculas
para compatibilidad con Railway (Linux/MySQL case-sensitive)

IMPORTANTE: Este script NO cambia los valores de datos (EST001, TIM001, etc.)
Solo cambia los nombres de objetos de base de datos.
"""

import re
import os

# Mapeo de nombres a convertir
TABLES = {
    'Tbl_Roles': 'tbl_roles',
    'Tbl_Usuario': 'tbl_usuario',
    'Tbl_UsuarioRol': 'tbl_usuariorol',
    'Tbl_Estado': 'tbl_estado',
    'Tbl_AreaReportante': 'tbl_areareportante',
    'Tbl_AreaResponsable': 'tbl_arearesponsable',
    'Tbl_Ubicacion': 'tbl_ubicacion',
    'Tbl_Riesgo': 'tbl_riesgo',
    'Tbl_DescripcionTipo': 'tbl_descripciontipo',
    'Tbl_Registro': 'tbl_registro',
    'Tbl_Asignacion': 'tbl_asignacion',
    'Tbl_TipoImagen': 'tbl_tipoimagen',
    'Tbl_EstadoImagen': 'tbl_estadoimagen',
    'Tbl_ImagenRegistro': 'tbl_imagenregistro',
    'Tbl_HistorialValidacion': 'tbl_historialvalidacion',
    'Tbl_Notificacion': 'tbl_notificacion',
}

STORED_PROCEDURES = {
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

def convert_sql_file(input_file, output_file):
    """Convierte un archivo SQL a minúsculas"""
    print(f"Procesando: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Convertir nombres de tablas
    for old_name, new_name in TABLES.items():
        # Usar word boundaries para evitar cambios parciales
        pattern = r'\b' + re.escape(old_name) + r'\b'
        content = re.sub(pattern, new_name, content)
    
    # Convertir nombres de stored procedures
    for old_name, new_name in STORED_PROCEDURES.items():
        pattern = r'\b' + re.escape(old_name) + r'\b'
        content = re.sub(pattern, new_name, content)
    
    # Guardar archivo convertido
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if content != original_content:
        print(f"  ✓ Convertido y guardado en: {output_file}")
    else:
        print(f"  - Sin cambios necesarios")
    
    return content != original_content

def main():
    """Función principal"""
    print("=" * 60)
    print("Conversión de nombres a minúsculas para Railway")
    print("=" * 60)
    print()
    
    # Archivos SQL a convertir
    sql_files = [
        'schema.sql',
        'fix_validar_imagen.sql',
        'fix_validar_final.sql',
        'update_sp_exportar.sql',
        'update_sp_validar.sql',
        'simplificar_estados.sql',
        'actualizar_sistema_completo.sql',
    ]
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    converted_count = 0
    
    for sql_file in sql_files:
        input_path = os.path.join(base_dir, sql_file)
        
        if not os.path.exists(input_path):
            print(f"⚠ Archivo no encontrado: {sql_file}")
            continue
        
        # Crear archivo con sufijo _lowercase
        output_path = os.path.join(base_dir, sql_file.replace('.sql', '_lowercase.sql'))
        
        if convert_sql_file(input_path, output_path):
            converted_count += 1
    
    print()
    print("=" * 60)
    print(f"Conversión completada: {converted_count} archivos convertidos")
    print("=" * 60)
    print()
    print("IMPORTANTE:")
    print("1. Los archivos originales NO fueron modificados")
    print("2. Los nuevos archivos tienen el sufijo '_lowercase.sql'")
    print("3. Revisa los archivos convertidos antes de usarlos")
    print("4. En Railway, ejecuta los archivos _lowercase.sql")
    print()
    print("Archivos convertidos:")
    for sql_file in sql_files:
        output_file = sql_file.replace('.sql', '_lowercase.sql')
        output_path = os.path.join(base_dir, output_file)
        if os.path.exists(output_path):
            print(f"  - {output_file}")

if __name__ == '__main__':
    main()
