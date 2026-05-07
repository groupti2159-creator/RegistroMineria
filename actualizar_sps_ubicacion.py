#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Actualizar todos los SPs para usar ubicacion como texto"""

from extensions import mysql
from app import app

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        print("Actualizando stored procedures...")
        with open('sql/actualizar_sps_ubicacion.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Ejecutar
        for statement in sql.split('$$'):
            statement = statement.strip()
            if statement and 'DELIMITER' not in statement and not statement.startswith('--'):
                try:
                    cur.execute(statement)
                    if 'DROP PROCEDURE' in statement:
                        sp_name = statement.split('IF EXISTS')[1].split('$')[0].strip()
                        print(f"  ✓ {sp_name}")
                except Exception as e:
                    if 'DELIMITER' not in str(e):
                        print(f"  ⚠ {e}")
        
        mysql.connection.commit()
        cur.close()
        print("\n✅ Todos los SPs actualizados")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
