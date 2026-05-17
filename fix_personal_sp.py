from app import app
from extensions import mysql

def fix_personal_api():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Crear SP que devuelve todo el personal sin filtro (para "personal responsable")
        cur.execute("DROP PROCEDURE IF EXISTS sp_obtener_todo_personal")
        
        sp_sql = """
        CREATE PROCEDURE sp_obtener_todo_personal()
        BEGIN
            SELECT 
                id,
                NombresCompletos,
                idareareportante
            FROM tbl_persona
            WHERE activo = 1
            ORDER BY NombresCompletos ASC;
        END
        """
        cur.execute(sp_sql)
        mysql.connection.commit()
        print("OK: sp_obtener_todo_personal creado")
        cur.close()

if __name__ == '__main__':
    fix_personal_api()
