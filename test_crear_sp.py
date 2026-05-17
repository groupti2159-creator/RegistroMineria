from app import app
from extensions import mysql
from datetime import datetime

def test_crear():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Verificar SP crearregistro primero
        cur.execute("SHOW CREATE PROCEDURE sp_crearregistro")
        sp_def = cur.fetchone()['Create Procedure']
        cur.fetchall()
        
        print("SP sp_crearregistro actual:")
        print(sp_def)
        print()
        
        # Contar parametros
        import re
        params = re.findall(r'IN \w+', sp_def)
        print(f"Numero de parametros IN: {len(params)}")
        for p in params:
            print(f"  {p}")
        
        cur.close()

if __name__ == '__main__':
    test_crear()
