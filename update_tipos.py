from extensions import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM tbl_descripciontipo')
    cur.execute('INSERT INTO tbl_descripciontipo (iddescripciontipo, descripciontipo) VALUES (1, "SEGURIDAD"), (2, "MEDIO AMBIENTE")')
    mysql.connection.commit()
    cur.execute('SELECT * FROM tbl_descripciontipo')
    print('=== TIPOS ACTUALIZADOS ===')
    for r in cur.fetchall():
        print(f'{r["iddescripciontipo"]}: {r["descripciontipo"]}')
    cur.close()
