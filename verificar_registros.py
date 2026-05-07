from extensions import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute('SELECT COUNT(*) as total FROM tbl_registro')
    total = cur.fetchone()['total']
    print(f'Total registros en BD: {total}')
    
    if total > 0:
        cur.execute('SELECT * FROM tbl_registro LIMIT 1')
        registro = cur.fetchone()
        print('\n=== PRIMER REGISTRO ===')
        for key, value in registro.items():
            print(f'{key}: {value}')
    
    cur.close()
