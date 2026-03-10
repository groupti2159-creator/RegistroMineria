"""
Script simple para verificar la conexión a la base de datos Railway
"""
from dotenv import load_dotenv
import os
import pymysql

load_dotenv()

def test_conexion():
    print("=" * 80)
    print("TEST DE CONEXIÓN A RAILWAY")
    print("=" * 80)
    
    # Mostrar configuración (sin mostrar password completo)
    host = os.getenv('MYSQL_HOST')
    user = os.getenv('MYSQL_USER')
    password = os.getenv('MYSQL_PASSWORD')
    database = os.getenv('MYSQL_DB')
    port = int(os.getenv('MYSQL_PORT', 3306))
    
    print(f"\nConfiguración:")
    print(f"  Host: {host}")
    print(f"  Puerto: {port}")
    print(f"  Usuario: {user}")
    print(f"  Base de datos: {database}")
    print(f"  Password: {'*' * (len(password) - 4) + password[-4:] if password else 'NO CONFIGURADO'}")
    
    print("\n" + "-" * 80)
    print("Intentando conectar...")
    print("-" * 80)
    
    try:
        # Intentar conexión
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            connect_timeout=10
        )
        
        print("\n✓ CONEXIÓN EXITOSA")
        
        # Obtener información del servidor
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"\n  MySQL Version: {version[0]}")
        
        cursor.execute("SELECT DATABASE()")
        db = cursor.fetchone()
        print(f"  Base de datos actual: {db[0]}")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n  Tablas encontradas: {len(tables)}")
        
        if tables:
            print("\n  Primeras 10 tablas:")
            for i, table in enumerate(tables[:10], 1):
                print(f"    {i}. {table[0]}")
            if len(tables) > 10:
                print(f"    ... y {len(tables) - 10} más")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 80)
        print("✓ CONEXIÓN VERIFICADA CORRECTAMENTE")
        print("=" * 80)
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"\n❌ ERROR DE CONEXIÓN:")
        print(f"   {e}")
        print("\nPosibles causas:")
        print("  1. Credenciales incorrectas en .env")
        print("  2. Servidor MySQL no está activo en Railway")
        print("  3. Firewall bloqueando la conexión")
        print("  4. Host o puerto incorrectos")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO:")
        print(f"   {e}")
        return False

if __name__ == '__main__':
    test_conexion()
