from app import app
from routes.desvios_ambientales.registro import get_maestros

with app.app_context():
    print('Llamando get_maestros()...')
    areas_rep, areas_res, ubicaciones, riesgos, tipos, estados, origenes = get_maestros()
    
    print(f'areas_rep: {len(areas_rep)}')
    print(f'areas_res: {len(areas_res)}')
    print(f'ubicaciones: {len(ubicaciones)}')
    print(f'riesgos: {len(riesgos)}')
    print(f'tipos: {len(tipos)}')
    print(f'estados: {len(estados)}')
    print(f'origenes: {len(origenes)}')
    
    print('\nDetalles de origenes:')
    for o in origenes:
        print(f'  - {o}')
