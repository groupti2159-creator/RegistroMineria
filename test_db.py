import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app
from extensions import mysql

def check_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        for t in ['tbl_comercializable', 'tbl_matpel', 'tbl_compostaje']:
            try:
                cur.execute(f"SELECT id, factura FROM {t} LIMIT 1")
                print(f"{t}: OK")
            except Exception as e:
                print(f"{t}: ERROR -> {e}")
        cur.close()

if __name__ == '__main__':
    check_db()
