from extensions import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM tbl_arearesponsable')
    print('=== AREAS RESPONSABLES ===')
    for r in cur.fetchall():
        print(f'{r["idarearesponsable"]}: {r["arearesponsable"]}')
    cur.close()
