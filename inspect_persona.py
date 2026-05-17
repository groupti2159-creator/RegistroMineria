from app import app
from extensions import mysql

def inspect():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Cuantos registros hay en tbl_persona
        cur.execute("SELECT COUNT(*) as total FROM tbl_persona WHERE activo=1")
        print(f"Total personas activas: {cur.fetchone()['total']}")
        
        # Listar todas con su area reportante
        cur.execute("""
            SELECT p.id, p.NombresCompletos, p.idareareportante, ar.areareportante
            FROM tbl_persona p
            LEFT JOIN tbl_areareportante ar ON ar.idareareportante = p.idareareportante
            WHERE p.activo = 1
            ORDER BY p.NombresCompletos
            LIMIT 20
        """)
        print("\nPersonas disponibles:")
        for r in cur.fetchall():
            print(f"  ID:{r['id']} - {r['NombresCompletos']} -> Area: {r['areareportante']} (id:{r['idareareportante']})")
        
        cur.close()

if __name__ == '__main__':
    inspect()
