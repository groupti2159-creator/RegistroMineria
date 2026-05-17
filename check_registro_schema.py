#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar el esquema de tbl_registro
"""

from app import app
from extensions import mysql

def check_schema():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Obtener el esquema de la tabla
            cur.execute("DESCRIBE tbl_registro")
            columns = cur.fetchall()
            
            print("Columnas en tbl_registro:")
            for col in columns:
                print(f"  - {col['Field']}: {col['Type']}")
            
            # Verificar si existe la columna origen
            has_origen = any(col['Field'] == 'idorigen' for col in columns)
            print(f"\n¿Tiene columna 'idorigen'? {has_origen}")
            
            cur.close()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    check_schema()
