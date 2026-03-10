"""
Script para aplicar automáticamente las correcciones a los stored procedures
"""
from dotenv import load_dotenv
import os
import pymysql

load_dotenv()

def aplicar_fix():
    print("=" * 80)
    print("APLICANDO CORRECCIONES A STORED PROCEDURES")
    print("=" * 80)
    
    # Leer el archivo SQL
    sql_file = 'fix_all_stored_procedures.sql'
    
    if not os.path.exists(sql_file):
        print(f"\n❌ Error: No se encuentra el archivo {sql_file}")
        print("Ejecuta primero: python generar_fix_all_sp.py")
        return False
    
    print(f"\nLeyendo archivo: {sql_file}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"Tamaño del archivo: {len(sql_content)} caracteres")
    
    try:
        # Conectar a la base de datos
        print("\nConectando a Railway...")
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB'),
            port=int(os.getenv('MYSQL_PORT', 3306))
        )
        
        print("✓ Conectado exitosamente")
        
        cursor = connection.cursor()
        
        # Dividir el SQL en statements individuales
        # Necesitamos manejar DELIMITER correctamente
        statements = []
        current_statement = []
        delimiter = ';'
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('--'):
                continue
            
            # Cambiar delimiter
            if line.startswith('DELIMITER'):
                delimiter = line.split()[1]
                continue
            
            current_statement.append(line)
            
            # Si la línea termina con el delimiter actual
            if line.endswith(delimiter):
                stmt = ' '.join(current_statement)
                # Remover el delimiter del final
                stmt = stmt[:-len(delimiter)].strip()
                if stmt:
                    statements.append(stmt)
                current_statement = []
        
        print(f"\nEjecutando {len(statements)} statements...")
        print("-" * 80)
        
        ejecutados = 0
        errores = 0
        
        for i, stmt in enumerate(statements, 1):
            # Mostrar solo el inicio del statement para no saturar la consola
            preview = stmt[:60] + '...' if len(stmt) > 60 else stmt
            
            try:
                cursor.execute(stmt)
                print(f"✓ {i}/{len(statements)}: {preview}")
                ejecutados += 1
            except Exception as e:
                print(f"❌ {i}/{len(statements)}: Error - {str(e)[:100]}")
                errores += 1
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("-" * 80)
        print(f"\n✓ Proceso completado:")
        print(f"  - Statements ejecutados: {ejecutados}")
        print(f"  - Errores: {errores}")
        
        if errores == 0:
            print("\n" + "=" * 80)
            print("✓ TODOS LOS STORED PROCEDURES CORREGIDOS EXITOSAMENTE")
            print("=" * 80)
            print("\nAhora puedes iniciar tu aplicación Flask:")
            print("  python app.py")
            return True
        else:
            print("\n⚠️  Algunos statements fallaron. Revisa los errores arriba.")
            return False
        
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")
        return False

if __name__ == '__main__':
    aplicar_fix()
