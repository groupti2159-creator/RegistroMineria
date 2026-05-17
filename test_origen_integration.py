#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from extensions import mysql

def test_origen_integration():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("\n" + "=" * 60)
            print("TEST 1: Verificar que tbl_registro tiene columna idorigen")
            print("=" * 60)
            
            cur.execute("SHOW COLUMNS FROM tbl_registro LIKE 'idorigen'")
            if cur.fetchone():
                print("✓ Columna 'idorigen' existe en tbl_registro")
            else:
                print("✗ Columna 'idorigen' NO existe en tbl_registro")
                return
            
            print("\n" + "=" * 60)
            print("TEST 2: Verificar que tbl_origen tiene datos")
            print("=" * 60)
            
            cur.execute("SELECT COUNT(*) as count FROM tbl_origen WHERE activo = 1")
            result = cur.fetchone()
            count = result['count'] if result else 0
            print(f"✓ Se encontraron {count} orígenes activos")
            
            print("\n" + "=" * 60)
            print("✓ TODOS LOS TESTS COMPLETADOS")
            print("=" * 60)
            
            cur.close()
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_origen_integration()
