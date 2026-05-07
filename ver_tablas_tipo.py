from extensions import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SHOW TABLES")
    print("=== TODAS LAS TABLAS ===")
    for r in cur.fetchall():
        tabla = list(r.values())[0]
        if 'tipo' in tabla.lower() or 'riesgo' in tabla.lower():
            print(f"  {tabla}")
            cur.execute(f"SELECT COUNT(*) as total FROM {tabla}")
            total = cur.fetchone()['total']
            print(f"    -> {total} registros")
    cur.close()
