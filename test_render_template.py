#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar que la plantilla recibe los datos correctamente
"""

from app import app
from extensions import mysql
from flask import render_template_string

def test_render():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("\n" + "=" * 60)
            print("TEST: Renderizando plantilla con origenes")
            print("=" * 60)
            
            # Obtener orígenes como lo hace get_maestros
            cur.execute("SELECT * FROM tbl_origen WHERE activo = 1 ORDER BY nombre")
            origenes = cur.fetchall()
            
            print(f"\n1. Orígenes obtenidos: {len(origenes)}")
            for o in origenes:
                print(f"   - {o}")
            
            # Crear un template de prueba
            template_str = """
            <select name="origen" class="form-select" required>
                <option value="">Seleccionar origen...</option>
                {% for o in origenes %}
                <option value="{{ o.idorigen }}">{{ o.nombre }}</option>
                {% endfor %}
            </select>
            """
            
            print("\n2. Renderizando template...")
            result = render_template_string(template_str, origenes=origenes)
            
            print("\n3. Resultado del render:")
            print(result)
            
            # Verificar que las opciones están en el resultado
            print("\n4. Verificando opciones en el resultado...")
            if "RAC" in result:
                print("   ✓ RAC encontrado")
            else:
                print("   ✗ RAC NO encontrado")
            
            if "INSPECCION" in result:
                print("   ✓ INSPECCION encontrado")
            else:
                print("   ✗ INSPECCION NO encontrado")
            
            if "EVENTO DE ALTO RIESGO" in result:
                print("   ✓ EVENTO DE ALTO RIESGO encontrado")
            else:
                print("   ✗ EVENTO DE ALTO RIESGO NO encontrado")
            
            cur.close()
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_render()
