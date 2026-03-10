"""
Script para generar SQL que corrija TODOS los stored procedures
convirtiendo referencias de tablas en mayúsculas a minúsculas
"""
from dotenv import load_dotenv
import os
import pymysql

load_dotenv()

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

def generar_fix_sql():
    print("=" * 80)
    print("GENERANDO SQL PARA CORREGIR STORED PROCEDURES")
    print("=" * 80)
    
    try:
        # Conectar a la base de datos
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        
        cursor = connection.cursor()
        
        # Obtener todos los stored procedures
        cursor.execute("SHOW PROCEDURE STATUS WHERE Db = DATABASE()")
        procedures = cursor.fetchall()
        
        sql_output = []
        sql_output.append("-- Script para corregir referencias de tablas en stored procedures")
        sql_output.append("-- Convierte Tbl_* a tbl_* para compatibilidad con Railway (Linux)")
        sql_output.append("-- Generado automáticamente\n")
        sql_output.append("USE desvios_ambientales;\n")
        
        sp_corregidos = 0
        sp_sin_cambios = 0
        
        for proc in procedures:
            sp_name = proc[1]  # Nombre del SP
            
            # Obtener definición del SP
            cursor.execute(f"SHOW CREATE PROCEDURE {sp_name}")
            result = cursor.fetchone()
            
            if result:
                create_statement = result[2]  # La definición completa
                
                # Verificar si tiene referencias a tablas en mayúsculas
                tiene_mayusculas = False
                for old_table in TABLES_MAP.keys():
                    if old_table in create_statement:
                        tiene_mayusculas = True
                        break
                
                if tiene_mayusculas:
                    print(f"✓ Corrigiendo: {sp_name}")
                    
                    # Reemplazar todas las referencias
                    fixed_statement = create_statement
                    for old_table, new_table in TABLES_MAP.items():
                        fixed_statement = fixed_statement.replace(old_table, new_table)
                    
                    # Agregar DROP y CREATE
                    sql_output.append(f"-- Corregir {sp_name}")
                    sql_output.append(f"DROP PROCEDURE IF EXISTS {sp_name};")
                    sql_output.append("")
                    sql_output.append("DELIMITER $$")
                    sql_output.append("")
                    sql_output.append(fixed_statement + "$$")
                    sql_output.append("")
                    sql_output.append("DELIMITER ;")
                    sql_output.append("")
                    
                    sp_corregidos += 1
                else:
                    print(f"  (sin cambios): {sp_name}")
                    sp_sin_cambios += 1
        
        cursor.close()
        connection.close()
        
        # Guardar el archivo SQL
        output_file = 'fix_all_stored_procedures.sql'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sql_output))
        
        print("\n" + "=" * 80)
        print(f"✓ Archivo generado: {output_file}")
        print(f"  - Stored procedures corregidos: {sp_corregidos}")
        print(f"  - Stored procedures sin cambios: {sp_sin_cambios}")
        print("=" * 80)
        print("\nPara aplicar los cambios, ejecuta:")
        print(f"  mysql -h {os.getenv('MYSQL_HOST')} -P {os.getenv('MYSQL_PORT')} \\")
        print(f"        -u {os.getenv('MYSQL_USER')} -p{os.getenv('MYSQL_PASSWORD')} \\")
        print(f"        {os.getenv('MYSQL_DB')} < {output_file}")
        print("\nO copia el contenido del archivo y ejecútalo en tu cliente MySQL")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == '__main__':
    generar_fix_sql()
