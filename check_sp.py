from app import app
from extensions import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute('SHOW CREATE PROCEDURE sp_crearregistro')
    result = cur.fetchone()
    if result:
        print(result['Create Procedure'])
    cur.close()
