"""
Script para verificar que las tablas y stored procedures en la base de datos
estén en minúsculas (compatible con Railway/Linux)
"""
from extensions import mysql
from app import app

def verificar_tablas():
    """Verifica que todas las tablas estén en minúsculas"""
    print("\n=== VERIFICANDO TABLAS ===")
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SHOW TABLES")
        tablas = cur.fetchall()
        cur.close()
        
        tablas_mayusculas = []
        for tabla in tablas:
            nombre_tabla = list(tabla.values())[0]
            if any(c.isupper() for c in nombre_tabla):
                tablas_mayusculas.append(nombre_tabla)
                print(f"❌ Tabla con mayúsculas: {nombre_tabla}")
            else:
                print(f"✓ {nombre_tabla}")
        
        if tablas_mayusculas:
            print(f"\n⚠️  Encontradas {len(tablas_mayusculas)} tablas con mayúsculas")
            print("Necesitas ejecutar el script de conversión en tu base de datos")
        else:
            print("\n✓ Todas las tablas están en minúsculas")

def verificar_stored_procedures():
    """Verifica que todos los stored procedures estén en minúsculas"""
    print("\n=== VERIFICANDO STORED PROCEDURES ===")
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SHOW PROCEDURE STATUS WHERE Db = DATABASE()")
        procedures = cur.fetchall()
        cur.close()
        
        sp_mayusculas = []
        for proc in procedures:
            nombre_sp = proc['Name']
            if any(c.isupper() for c in nombre_sp):
                sp_mayusculas.append(nombre_sp)
                print(f"❌ SP con mayúsculas: {nombre_sp}")
            else:
                print(f"✓ {nombre_sp}")
        
        if sp_mayusculas:
            print(f"\n⚠️  Encontrados {len(sp_mayusculas)} stored procedures con mayúsculas")
            print("Necesitas ejecutar el script de conversión en tu base de datos")
        else:
            print("\n✓ Todos los stored procedures están en minúsculas")

def verificar_contenido_sp():
    """Verifica el contenido del SP sp_login para ver si tiene referencias a tablas en mayúsculas"""
    print("\n=== VERIFICANDO CONTENIDO DE sp_login ===")
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SHOW CREATE PROCEDURE sp_login")
        result = cur.fetchone()
        cur.close()
        
        if result:
            contenido = result['Create Procedure']
            print("\nContenido del stored procedure sp_login:")
            print("-" * 80)
            print(contenido)
            print("-" * 80)
            
            # Buscar referencias a tablas en mayúsculas
            tablas_mayusculas = ['Tbl_Usuario', 'Tbl_UsuarioRol', 'Tbl_Roles']
            referencias_encontradas = []
            for tabla in tablas_mayusculas:
                if tabla in contenido:
                    referencias_encontradas.append(tabla)
            
            if referencias_encontradas:
                print(f"\n❌ El SP contiene referencias a tablas en mayúsculas:")
                for ref in referencias_encontradas:
                    print(f"   - {ref}")
                print("\n⚠️  Necesitas actualizar el stored procedure en la base de datos")
            else:
                print("\n✓ El SP no contiene referencias a tablas en mayúsculas")

if __name__ == '__main__':
    try:
        print("=" * 80)
        print("VERIFICACIÓN DE BASE DE DATOS PARA RAILWAY")
        print("=" * 80)
        
        verificar_tablas()
        verificar_stored_procedures()
        verificar_contenido_sp()
        
        print("\n" + "=" * 80)
        print("VERIFICACIÓN COMPLETADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error de conexión: {e}")
        print("\nVerifica que:")
        print("1. Las credenciales en .env sean correctas")
        print("2. El servidor MySQL en Railway esté activo")
        print("3. El puerto y host sean correctos")
