from app import app
from extensions import mysql

def inspect():
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("CALL sp_listarregistros(NULL)")
        rows = cur.fetchall()
        print("Registros desde SP:")
        for r in rows:
            print(f"  ID: {r.get('IdRegistro') or r.get('idregistro')}, "
                  f"Código: {r.get('Codigo') or r.get('codigo')}, "
                  f"CCTA: {r.get('cctaresponsable')}, "
                  f"NombreCctaResponsable: {r.get('NombreCctaResponsable') or r.get('nombrecctaresponsable')}")
        cur.close()

if __name__ == '__main__':
    inspect()
