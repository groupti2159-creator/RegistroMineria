#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para debuggear la carga de orígenes
"""

from app import app
from extensions import mysql

def debug_origenes():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("\n" + "=" * 60)
            print("DEBUG: Verificando carga de orígenes")
            print("=" * 60)
            
            # Test 1: Verificar que la tabla existe
            print("\n1. Verificando que tbl_origen existe...")
            cur.execute("SHOW TABLES LIKE 'tbl_origen'")
            if cur.fetchone():
                print("   ✓ Tabla existe")
            else:
                print("   ✗ Tabla NO existe")
                return
            
            # Test 2: Contar registros
            print("\n2. Contando registros en tbl_origen...")
            cur.execute("SELECT COUNT(*) as count FROM tbl_origen")
            result = cur.fetchone()
            total = result['count'] if result else 0
            print(f"   Total de registros: {total}")
            
            # Test 3: Contar registros activos
            print("\n3. Contando registros activos (activo = 1)...")
            cur.execute("SELECT COUNT(*) as count FROM tbl_origen WHERE activo = 1")
            result = cur.fetchone()
            activos = result['count'] if result else 0
            print(f"   Total activos: {activos}")
            
            # Test 4: Obtener todos los registros
            print("\n4. Obteniendo todos los registros...")
            cur.execute("SELECT * FROM tbl_origen")
            all_records = cur.fetchall()
            for record in all_records:
                print(f"   - ID: {record.get('idorigen')}, Nombre: {record.get('nombre')}, Activo: {record.get('activo')}")
            
            # Test 5: Obtener solo activos (como en get_maestros)
            print("\n5. Obteniendo solo registros activos (como en get_maestros)...")
            cur.execute("SELECT * FROM tbl_origen WHERE activo = 1 ORDER BY nombre")
            origenes = cur.fetchall()
            print(f"   Registros retornados: {len(origenes)}")
            for o in origenes:
                print(f"   - ID: {o.get('idorigen')}, Nombre: {o.get('nombre')}")
                print(f"     Tipo: {type(o)}")
                print(f"     Keys: {o.keys() if hasattr(o, 'keys') else 'N/A'}")
            
            # Test 6: Verificar estructura de datos
            print("\n6. Verificando estructura de datos...")
            if origenes:
                first = origenes[0]
                print(f"   Primer registro: {first}")
                print(f"   Tipo: {type(first)}")
                if hasattr(first, 'keys'):
                    print(f"   Keys disponibles: {list(first.keys())}")
                    print(f"   idorigen: {first.get('idorigen')}")
                    print(f"   nombre: {first.get('nombre')}")
            
            cur.close()
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_origenes()
