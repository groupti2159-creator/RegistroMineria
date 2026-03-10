"""
Script para corregir el dump SQL y convertir todas las referencias
de tablas en mayúsculas a minúsculas dentro de los stored procedures
"""
import re

# Mapeo de tablas (mayúsculas -> minúsculas)
TABLES_MAP = {
    'Tbl_Usuario': 'tbl_usuario',
    'Tbl_UsuarioRol': 'tbl_usuariorol',
    'Tbl_Roles': 'tbl_roles',
    'Tbl_Registro': 'tbl_registro',
    'Tbl_ImagenRegistro': 'tbl_imagenregistro',
    'Tbl_Estado': 'tbl_estado',
    'Tbl_EstadoImagen': 'tbl_estadoimagen',
    'Tbl_TipoImagen': 'tbl_tipoimagen',
    'Tbl_AreaReportante': 'tbl_areareportante',
    'Tbl_AreaResponsable': 'tbl_arearesponsable',
    'Tbl_Ubicacion': 'tbl_ubicacion',
    'Tbl_Riesgo': 'tbl_riesgo',
    'Tbl_DescripcionTipo': 'tbl_descripciontipo',
    'Tbl_Notificacion': 'tbl_notificacion',
    'Tbl_HistorialAprobacion': 'tbl_historialaprobacion',
    'Tbl_Asignacion': 'tbl_asignacion',
}

def fix_dump_file(input_file, output_file):
    """Lee el dump SQL y corrige las referencias a tablas en mayúsculas"""
    
    print("=" * 80)
    print("CORRIGIENDO DUMP SQL")
    print("=" * 80)
    print(f"\nArchivo de entrada: {input_file}")
    print(f"Archivo de salida: {output_file}")
    
    try:
        # Leer el archivo
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\nTamaño original: {len(content)} caracteres")
        
        # Contar reemplazos
        total_replacements = 0
        replacements_by_table = {}
        
        # Reemplazar cada tabla
        for old_table, new_table in TABLES_MAP.items():
            count = content.count(old_table)
            if count > 0:
                content = content.replace(old_table, new_table)
                replacements_by_table[old_table] = count
                total_replacements += count
        
        # Guardar el archivo corregido
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✓ Archivo corregido guardado")
        print(f"Tamaño final: {len(content)} caracteres")
        print(f"\nReemplazos realizados: {total_replacements}")
        
        if replacements_by_table:
            print("\nDetalle de reemplazos:")
            for table, count in sorted(replacements_by_table.items()):
                print(f"  {table} -> {TABLES_MAP[table]}: {count} veces")
        
        print("\n" + "=" * 80)
        print("✓ DUMP SQL CORREGIDO EXITOSAMENTE")
        print("=" * 80)
        print(f"\nAhora puedes importar el archivo: {output_file}")
        print("En Railway o en tu base de datos local")
        
        return True
        
    except FileNotFoundError:
        print(f"\n❌ Error: No se encuentra el archivo {input_file}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    # Puedes cambiar estos nombres de archivo según necesites
    input_file = 'dump_original.sql'  # Tu dump actual
    output_file = 'dump_corregido.sql'  # El dump corregido
    
    print("\nNOTA: Asegúrate de tener tu dump SQL en el mismo directorio")
    print(f"      con el nombre '{input_file}'")
    print("\nO edita este script para usar el nombre correcto de tu archivo\n")
    
    fix_dump_file(input_file, output_file)
