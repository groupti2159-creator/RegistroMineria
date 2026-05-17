from app import app
from routes.desvios_ambientales.registro import registrar

def test_render():
    with app.test_client() as client:
        # We need to mock session for admin
        with client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['accesos'] = ['DESVIOS']
            sess['usuario_rol'] = 1
        
        response = client.get('/admin/registrar')
        html = response.data.decode('utf-8')
        
        # Look for 001-03 or 001-02 rows in the rendered html
        print("Buscando en HTML:")
        import re
        rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
        for r in rows:
            if '001-03' in r or '001-02' in r:
                print("="*40)
                print(r.strip())
                print("="*40)

if __name__ == '__main__':
    test_render()
