from app import app
from extensions import mysql
from routes.desvios_ambientales.registro import get_maestros

def test_full_flow():
    with app.app_context():
        try:
            print('\n' + '=' * 60)
            print('TEST: Flujo completo de carga de página')
            print('=' * 60)
            
            print('\n1. Llamando get_maestros()...')
            areas_rep, areas_res, ubicaciones, riesgos, tipos, estados, origenes = get_maestros()
            
            print(f'\n2. Resultados:')
            print(f'   - origenes: {len(origenes)} registros')
            
            print(f'\n3. Detalles de origenes:')
            for o in origenes:
                print(f'   - {o}')
            
            if len(origenes) == 0:
                print('\n✗ ERROR: origenes está vacío!')
                return False
            else:
                print(f'\n✓ origenes tiene {len(origenes)} registros')
            
            print(f'\n✓ TEST COMPLETADO EXITOSAMENTE')
            return True
            
        except Exception as e:
            print(f'✗ Error: {e}')
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_full_flow()
    exit(0 if success else 1)
