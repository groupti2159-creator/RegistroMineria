#!/usr/bin/env python
import sys
sys.path.insert(0, 'd:\\Minera\\RegistroMineria')

try:
    print("1. Importando app...")
    from app import app
    print("   ✓ App importada")
    
    print("\n2. Creando cliente de prueba...")
    client = app.test_client()
    print("   ✓ Cliente creado")
    
    print("\n3. Probando creación de proyecto...")
    response = client.post('/admin/proyectos/crear', 
        json={
            'nombre': 'Proyecto Test',
            'descripcion': 'Descripción de prueba'
        },
        headers={'Content-Type': 'application/json'}
    )
    print(f"   Status: {response.status_code}")
    
    # Manejar redirects
    if response.status_code in (301, 302, 303, 307, 308):
        print(f"   Redirect a: {response.location}")
        print("   ✓ Redirección recibida (esperado para POST sin sesión)")
    else:
        result = response.get_json()
        print(f"   Resultado: {result}")
        
        if result and result.get('success'):
            print(f"   ✓ Proyecto creado con ID: {result['proyecto']['idproyecto']}")
        else:
            print(f"   ✗ Error: {result.get('error') if result else 'Sin respuesta JSON'}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
