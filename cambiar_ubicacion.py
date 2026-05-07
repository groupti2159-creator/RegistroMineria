#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cambiar campo ubicacion a texto libre"""

from extensions import mysql
from app import app

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        print("Eliminando foreign key...")
        try:
            cur.execute("ALTER TABLE tbl_registro DROP FOREIGN KEY fk_reg_ubic")
            print("  ✓ Foreign key eliminada")
        except Exception as e:
            print(f"  ⚠ {e}")
        
        print("Cambiando tipo de dato...")
        cur.execute("ALTER TABLE tbl_registro MODIFY COLUMN idubicacion VARCHAR(200) NOT NULL")
        
        print("Renombrando columna...")
        cur.execute("ALTER TABLE tbl_registro CHANGE COLUMN idubicacion ubicacion VARCHAR(200) NOT NULL")
        
        mysql.connection.commit()
        print("✓ Campo actualizado")
        
        # Verificar
        cur.execute("DESCRIBE tbl_registro")
        print("\n=== Campo ubicacion ===")
        for col in cur.fetchall():
            if 'ubicacion' in col['Field'].lower():
                print(f"  {col['Field']:30s} {col['Type']:20s}")
        
        cur.close()
        print("\n✅ Proceso completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
