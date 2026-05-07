#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crear tabla de riesgos críticos"""

from extensions import mysql
from app import app

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        with open('sql/crear_tabla_riesgos_criticos.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Ejecutar cada statement
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cur.execute(statement)
                except Exception as e:
                    print(f"⚠ {e}")
        
        mysql.connection.commit()
        
        # Verificar
        cur.execute("SELECT tipo_asociado, COUNT(*) as total FROM tbl_riesgos_criticos GROUP BY tipo_asociado")
        print("\n=== RIESGOS CRÍTICOS CREADOS ===")
        for row in cur.fetchall():
            tipo = "SEGURIDAD" if row['tipo_asociado'] == 1 else "MEDIO AMBIENTE"
            print(f"  {tipo}: {row['total']} riesgos")
        
        cur.close()
        print("\n✅ Tabla creada exitosamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
