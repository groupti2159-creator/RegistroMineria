from app import app
from extensions import mysql

SPS = [
    'sp_detalleregistro',
    'sp_imagenesregistro',
    'sp_listarregistros',
    'sp_guardarimagen',
]

def inspect():
    with app.app_context():
        cur = mysql.connection.cursor()
        for sp in SPS:
            print(f"\n{'='*60}")
            print(f"SP: {sp}")
            print('='*60)
            try:
                cur.execute(f"SHOW CREATE PROCEDURE {sp}")
                row = cur.fetchone()
                if row:
                    print(row['Create Procedure'])
                cur.fetchall()
            except Exception as e:
                print(f"ERROR: {e}")
        cur.close()

if __name__ == '__main__':
    inspect()
