#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Agregar campo personalreportante a tbl_registro"""

from extensions import mysql
from app import app

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        print("Agregando campo personalreportante...")
        cur.execute("""
            ALTER TABLE tbl_registro 
            ADD COLUMN personalreportante INT NULL AFTER idareareportante
        """)
        
        print("Agregando foreign key...")
        cur.execute("""
            ALTER TABLE tbl_registro
            ADD CONSTRAINT fk_personal_reportante 
                FOREIGN KEY (personalreportante) 
                REFERENCES tbl_persona(id) 
                ON DELETE SET NULL
        """)
        
        mysql.connection.commit()
        print("✓ Campo agregado exitosamente")
        
        # Verificar
        cur.execute("DESCRIBE tbl_registro")
        print("\n=== CAMPOS RELACIONADOS ===")
        for col in cur.fetchall():
            if 'personal' in col['Field'].lower() or 'area' in col['Field'].lower():
                print(f"  {col['Field']:30s} {col['Type']:20s}")
        
        cur.close()
        print("\n✅ Proceso completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
