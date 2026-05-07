#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Drop y recrear SPs"""

from extensions import mysql
from app import app

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        sps = [
            'SP_ListarRegistros',
            'SP_ListarRegistrosSupervisor', 
            'SP_DetalleRegistro',
            'SP_HistorialAdmin',
            'SP_HistorialSupervisor',
            'SP_ExportarExcel',
            'SP_ActualizarRegistro'
        ]
        
        print("Eliminando SPs...")
        for sp in sps:
            try:
                cur.execute(f"DROP PROCEDURE IF EXISTS {sp}")
                print(f"  ✓ {sp} eliminado")
            except Exception as e:
                print(f"  ⚠ {sp}: {e}")
        
        mysql.connection.commit()
        
        print("\nCreando SPs actualizados...")
        with open('sql/actualizar_sps_ubicacion.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Remover DELIMITER y DROP
        sql = sql.replace('DELIMITER $$', '').replace('DELIMITER ;', '')
        sql = '\n'.join([line for line in sql.split('\n') if not line.strip().startswith('DROP PROCEDURE')])
        
        # Ejecutar cada CREATE PROCEDURE
        procedures = sql.split('CREATE PROCEDURE')
        for proc in procedures[1:]:  # Skip first empty
            try:
                cur.execute('CREATE PROCEDURE' + proc.split('$$')[0])
                sp_name = proc.split('(')[0].strip()
                print(f"  ✓ {sp_name} creado")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        
        mysql.connection.commit()
        cur.close()
        print("\n✅ Proceso completado")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
