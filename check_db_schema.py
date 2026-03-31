from app import app
from extensions import mysql

def check_db():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            cur.execute("DESCRIBE tbl_proyecto")
            print("--- tbl_proyecto ---")
            for row in cur.fetchall():
                print(row)
            
            cur.execute("DESCRIBE tbl_roles")
            print("\n--- tbl_roles ---")
            for row in cur.fetchall():
                print(row)
            
            cur.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
