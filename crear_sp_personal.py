#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para crear el stored procedure sp_obtener_personal_por_area"""

from extensions import mysql
from app import app

def crear_sp():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("Creando stored procedure sp_obtener_personal_por_area...")
            
            # Leer el archivo SQL
            with open('sql/sp_obtener_personal_por_area.sql', 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Ejecutar cada statement
            statements = sql_content.split('$$')
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--') and statement != 'DELIMITER':
                    try:
                        cur.execute(statement)
                    except Exception as e:
                        if 'DELIMITER' not in str(e):
                            print(f"  ⚠ Warning: {e}")
            
            mysql.connection.commit()
            print("  ✓ Stored procedure creado")
            
            # Probar el SP
            print("\n=== PRUEBA: Personal de MINA (id=12) ===")
            cur.callproc('sp_obtener_personal_por_area', (12,))
            for result in cur.stored_results():
                personas = result.fetchall()
                for p in personas:
                    print(f"  {p['id']:3d}: {p['NombresCompletos']}")
                print(f"\nTotal: {len(personas)} personas")
            
            cur.close()
            print("\n✅ Proceso completado")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    crear_sp()
