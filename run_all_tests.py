#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ejecutar y depurar todos los archivos de prueba
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_imports():
    """Verificar que todos los imports funcionan correctamente"""
    print("\n" + "="*60)
    print("TEST 1: Verificar imports")
    print("="*60)
    
    try:
        print("  [OK] Importando app...")
        from app import app
        
        print("  [OK] Importando get_maestros...")
        from routes.desvios_ambientales.registro import get_maestros
        
        print("  [OK] Importando mysql...")
        from extensions import mysql
        
        print("  [OK] Todos los imports funcionan correctamente")
        return True
    except Exception as e:
        print(f"  [ERROR] Error en imports: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_maestros():
    """Verificar que get_maestros() retorna los datos correctos"""
    print("\n" + "="*60)
    print("TEST 2: Verificar get_maestros()")
    print("="*60)
    
    try:
        from app import app
        from routes.desvios_ambientales.registro import get_maestros
        
        with app.app_context():
            print("  Llamando get_maestros()...")
            areas_rep, areas_res, ubicaciones, riesgos, tipos, estados, origenes = get_maestros()
            
            print(f"  - areas_rep: {len(areas_rep)} registros")
            print(f"  - areas_res: {len(areas_res)} registros")
            print(f"  - ubicaciones: {len(ubicaciones)} registros")
            print(f"  - riesgos: {len(riesgos)} registros")
            print(f"  - tipos: {len(tipos)} registros")
            print(f"  - estados: {len(estados)} registros")
            print(f"  - origenes: {len(origenes)} registros")
            
            # Verificar que origenes tiene datos
            if len(origenes) == 0:
                print("  [ERROR] origenes está vacío!")
                return False
            
            print("\n  Detalles de origenes:")
            for o in origenes:
                print(f"    - ID: {o.get('idorigen')}, Nombre: {o.get('nombre')}")
            
            print("  [OK] get_maestros() funciona correctamente")
            return True
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Verificar que la conexión a la base de datos funciona"""
    print("\n" + "="*60)
    print("TEST 3: Verificar conexión a base de datos")
    print("="*60)
    
    try:
        from app import app
        from extensions import mysql
        
        with app.app_context():
            print("  Intentando conectar a la base de datos...")
            cur = mysql.connection.cursor()
            cur.execute("SELECT COUNT(*) as count FROM tbl_origen WHERE activo = 1")
            result = cur.fetchone()
            cur.close()
            
            count = result.get('count') if isinstance(result, dict) else result[0]
            print(f"  - Orígenes activos en BD: {count}")
            
            if count == 0:
                print("  [ERROR] No hay orígenes en la base de datos!")
                return False
            
            print("  [OK] Conexión a base de datos funciona correctamente")
            return True
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_structure():
    """Verificar que la estructura de archivos es correcta"""
    print("\n" + "="*60)
    print("TEST 4: Verificar estructura de archivos")
    print("="*60)
    
    required_files = [
        'routes/desvios_ambientales/registro.py',
        'templates/desvios_ambientales/desvios.html',
        'static/js/desvios_ambientales/desvios.js',
        'tests/test_desvios_ambientales.py',
        'tests/pages/desvios_page.py',
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        exists = os.path.exists(full_path)
        status = "[OK]" if exists else "[ERROR]"
        print(f"  {status} {file_path}")
        if not exists:
            all_exist = False
    
    if all_exist:
        print("  [OK] Todos los archivos requeridos existen")
        return True
    else:
        print("  [ERROR] Faltan algunos archivos")
        return False


def main():
    """Ejecutar todos los tests"""
    print("\n" + "="*60)
    print("DEPURACION DE ARCHIVOS DE PRUEBA")
    print("="*60)
    
    results = {
        "Imports": test_imports(),
        "get_maestros()": test_get_maestros(),
        "Conexión BD": test_database_connection(),
        "Estructura archivos": test_file_structure(),
    }
    
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    
    for test_name, result in results.items():
        status = "[PASO]" if result else "[FALLO]"
        print(f"  {status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("[OK] TODOS LOS TESTS PASARON")
    else:
        print("[ERROR] ALGUNOS TESTS FALLARON")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
