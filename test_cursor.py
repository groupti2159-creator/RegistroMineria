import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app
from extensions import mysql

def test_cursor():
    with app.app_context():
        try:
            with mysql.connection.cursor() as cur:
                cur.execute("SELECT 1 AS test")
                res = cur.fetchone()
                print("Context manager works!", res)
            print("Cursor auto-closed successfully")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == '__main__':
    test_cursor()
