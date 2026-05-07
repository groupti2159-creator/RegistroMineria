#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para agregar nuevas áreas reportantes"""

from extensions import mysql
from app import app

def agregar_areas():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            areas = [
                'GERENCIA DE OPERACIONES',
                'MANTTO ELECTRICO',
                'GEOLOGIA Y EXPLORACION',
                'BIENESTAR SOCIAL',
                'MANTENIMIENTO MECANICO',
                'MINA',
                'OBRAS CIVILES',
                'PLANEAMIENTO',
                'PLANTA',
                'PROYECTOS',
                'RECURSOS HUMANOS',
                'SSOMA',
                'PROTECCION INTERNA'
            ]
            
            print("Agregando áreas reportantes...")
            for area in areas:
                cur.execute(
                    "INSERT IGNORE INTO tbl_areareportante (areareportante) VALUES (%s)",
                    (area,)
                )
                print(f"  ✓ {area}")
            
            mysql.connection.commit()
            
            # Mostrar todas las áreas
            print("\n=== ÁREAS REPORTANTES ACTUALES ===")
            cur.execute("SELECT * FROM tbl_areareportante ORDER BY areareportante")
            for row in cur.fetchall():
                print(f"{row['idareareportante']:3d}: {row['areareportante']}")
            
            cur.close()
            print("\n✅ Áreas agregadas exitosamente")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    agregar_areas()
