#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Actualizar SP_CrearRegistro"""

from extensions import mysql
from app import app

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        print("Actualizando SP_CrearRegistro...")
        with open('sql/actualizar_sp_crearregistro.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Ejecutar
        for statement in sql.split('$$'):
            statement = statement.strip()
            if statement and 'DELIMITER' not in statement and not statement.startswith('--'):
                try:
                    cur.execute(statement)
                except Exception as e:
                    if 'DELIMITER' not in str(e):
                        print(f"  ⚠ {e}")
        
        mysql.connection.commit()
        cur.close()
        print("✅ SP actualizado exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
