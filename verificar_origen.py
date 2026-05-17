#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar que la tabla tbl_origen tiene datos
"""

from app import app
from extensions import mysql

def verificar_origen():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Verificar que la tabla existe
            cur.execute("SHOW TABLES LIKE 'tbl_origen'")
            if not cur.fetchone():
                print("✗ La tabla tbl_origen no existe")
                return
            
            print("✓ La tabla tbl_origen existe")
            
            # Obtener los datos
            cur.execute("SELECT * FROM tbl_origen WHERE activo = 1 ORDER BY nombre")
            origenes = cur.fetchall()
            
            print(f"\n✓ Se encontraron {len(origenes)} orígenes activos:")
            for o in origenes:
                print(f"  - ID: {o['idorigen']}, Nombre: {o['nombre']}")
            
            if len(origenes) == 0:
                print("\n✗ No hay orígenes activos en la tabla")
            
            cur.close()
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    verificar_origen()
