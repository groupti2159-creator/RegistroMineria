from app import app
from extensions import mysql

def inspect():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("SHOW CREATE PROCEDURE sp_actualizarregistro")
        row = cur.fetchone()
        if row:
            print(row['Create Procedure'])
        cur.close()

if __name__ == '__main__':
    inspect()
