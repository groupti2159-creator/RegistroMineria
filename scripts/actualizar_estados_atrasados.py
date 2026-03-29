#!/usr/bin/env python3
"""
Script para actualizar estados atrasados en la base de datos.
Puede ejecutarse como cron job para mantener los estados actualizados.

Uso:
    python actualizar_estados_atrasados.py

Cron job (ejecutar cada hora):
    0 * * * * cd /ruta/a/ecosupervisor && python actualizar_estados_atrasados.py >> logs/estados_atrasados.log 2>&1
"""

import os
import sys
from datetime import datetime

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import mysql
from app import app

def actualizar_estados_atrasados():
    """
    Actualiza los estados de registros pendientes con fecha de ejecución vencida.
    """
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            
            # Llamar al stored procedure
            cur.callproc('SP_ActualizarEstadosAtrasados')
            
            # Obtener el resultado
            result = cur.fetchone()
            registros_actualizados = result['registros_actualizados'] if result else 0
            
            mysql.connection.commit()
            cur.close()
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] ✓ Actualización completada: {registros_actualizados} registros marcados como 'Atrasado'")
            
            return registros_actualizados
            
    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] ✗ Error al actualizar estados: {str(e)}", file=sys.stderr)
        return -1

if __name__ == '__main__':
    print("=" * 60)
    print("Actualizando estados atrasados...")
    print("=" * 60)
    
    resultado = actualizar_estados_atrasados()
    
    if resultado >= 0:
        sys.exit(0)  # Éxito
    else:
        sys.exit(1)  # Error
