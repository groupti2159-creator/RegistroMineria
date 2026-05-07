#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para renombrar tabla tbl_personas a tbl_persona"""

from extensions import mysql
from app import app

def renombrar_tabla():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("Renombrando tabla tbl_personas a tbl_persona...")
            cur.execute("RENAME TABLE tbl_personas TO tbl_persona")
            mysql.connection.commit()
            print("  ✓ Tabla renombrada exitosamente")
            
            # Verificar
            cur.execute("SHOW TABLES LIKE 'tbl_persona%'")
            tablas = cur.fetchall()
            print("\n=== TABLAS ENCONTRADAS ===")
            for tabla in tablas:
                nombre = list(tabla.values())[0]
                print(f"  ✓ {nombre}")
            
            # Contar registros
            cur.execute("SELECT COUNT(*) as total FROM tbl_persona")
            total = cur.fetchone()['total']
            print(f"\nTotal de registros en tbl_persona: {total}")
            
            cur.close()
            print("\n✅ Proceso completado")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    renombrar_tabla()
