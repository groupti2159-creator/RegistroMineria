from extensions import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SHOW TABLES")
    print("=== TABLAS EN LA BASE DE DATOS ===")
    for row in cur.fetchall():
        tabla = list(row.values())[0]
        if 'area' in tabla.lower():
            print(f"  ✓ {tabla}")
    cur.close()
