from app import app
from extensions import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute('DESCRIBE tbl_registro')
    columns = cur.fetchall()
    
    print('Columnas en tbl_registro:')
    for col in columns:
        field = col['Field']
        tipo = col['Type']
        if 'ubicacion' in field.lower():
            print('  - ' + field + ': ' + tipo)
    
    cur.close()
