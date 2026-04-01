#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para insertar datos de prueba en la tabla tbl_registroana
"""

import sys
from extensions import mysql
from app import app

def insertar_datos_ana():
    """Inserta 10 registros de prueba en tbl_registroana"""
    
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Primero, verificar la estructura de la tabla
            print("[INFO] Verificando estructura de la tabla...")
            cur.execute("DESCRIBE tbl_registroana")
            columnas = cur.fetchall()
            print("\n[COLUMNAS] tbl_registroana:")
            for col in columnas:
                print(f"   - {col['Field']} ({col['Type']})")
            
            # Verificar cuántos registros hay actualmente
            cur.execute("SELECT COUNT(*) as total FROM tbl_registroana")
            count_antes = cur.fetchone()['total']
            print(f"\n[REGISTROS] Actuales: {count_antes}")
            
            # Usar el stored procedure que ya existe
            print("\n[INSERTANDO] Usando sp_crearregistroana...")
            
            datos = [
                # Enero 2026
                ('2026-01-15', '24 horas', 14500.00, 14508.50, 8.50, 0.000098380),
                ('2026-01-16', '24 horas', 14508.50, 14517.20, 8.70, 0.000100694),
                ('2026-01-17', '24 horas', 14517.20, 14525.80, 8.60, 0.000099537),
                
                # Febrero 2026
                ('2026-02-10', '24 horas', 14600.00, 14608.92, 8.92, 0.000103241),
                ('2026-02-11', '24 horas', 14608.92, 14617.50, 8.58, 0.000099306),
                ('2026-02-12', '24 horas', 14617.50, 14626.10, 8.60, 0.000099537),
                
                # Marzo 2026
                ('2026-03-05', '24 horas', 14700.00, 14708.75, 8.75, 0.000101273),
                ('2026-03-06', '24 horas', 14708.75, 14717.40, 8.65, 0.000100116),
                ('2026-03-07', '24 horas', 14717.40, 14726.00, 8.60, 0.000099537),
                ('2026-03-08', '24 horas', 14726.00, 14734.80, 8.80, 0.000101852),
            ]
            
            insertados = 0
            for dato in datos:
                try:
                    cur.callproc('sp_crearregistroana', dato)
                    insertados += 1
                    print(f"   [OK] {dato[0]}")
                except Exception as e:
                    print(f"   [ERROR] {dato[0]}: {e}")
            
            mysql.connection.commit()
            
            # Verificar cuántos registros hay ahora
            cur.execute("SELECT COUNT(*) as total FROM tbl_registroana")
            count_despues = cur.fetchone()['total']
            
            print(f"\n[RESULTADO] Insertados: {insertados} registros")
            print(f"[TOTAL] Registros ahora: {count_despues}")
            
            # Mostrar los últimos 5 registros
            if count_despues > 0:
                print("\n[ULTIMOS 5 REGISTROS]:")
                cur.execute("""
                    SELECT *
                    FROM tbl_registroana
                    ORDER BY FechaRegistro DESC
                    LIMIT 5
                """)
                
                for row in cur.fetchall():
                    fecha = row.get('Fecha') or row.get('fecha')
                    vol = row.get('VolumenM3') or row.get('volumenm3') or 'N/A'
                    print(f"   Fecha: {fecha} | Vol: {vol} m3")
            
            cur.close()
            print("\n[COMPLETADO] Proceso finalizado")
            return insertados > 0
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  INSERTAR DATOS DE PRUEBA - Reporte ANA")
    print("="*60 + "\n")
    
    exito = insertar_datos_ana()
    
    if exito:
        print("\n[EXITO] Proceso completado exitosamente")
        print("   Ahora puedes ejecutar los tests con: pytest tests/")
        sys.exit(0)
    else:
        print("\n[FALLO] Hubo errores al insertar los datos")
        sys.exit(1)
