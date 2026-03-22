from dotenv import load_dotenv
load_dotenv()  # Carga .env ANTES de leer Config

from flask import Flask
from extensions import mysql
from config import Config
import os

app = Flask(__name__)

# Cargar configuración
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Imprimir configuración para debug
Config.print_config()

# Configurar MySQL
mysql.init_app(app)

from routes.auth       import auth_bp
from routes.admin      import admin_bp
from routes.desvios_ambientales import da_bp
from routes.gestion_residuos    import gr_bp
from routes.compromisos         import compromisos_bp
from routes.meteorologia        import meteorologia_bp
from routes.supervisor import supervisor_bp
from routes.shared     import shared_bp
from routes.proyectos  import proyectos_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp,        url_prefix='/admin')
app.register_blueprint(da_bp,           url_prefix='/admin')
app.register_blueprint(gr_bp,           url_prefix='/admin')
app.register_blueprint(compromisos_bp,  url_prefix='/admin')
app.register_blueprint(meteorologia_bp, url_prefix='/admin')
app.register_blueprint(supervisor_bp,   url_prefix='/supervisor')
app.register_blueprint(shared_bp,       url_prefix='/api')
app.register_blueprint(proyectos_bp,    url_prefix='/proyectos')

from flask import session
from routes.auth import cargar_accesos, cargar_modulos

@app.before_request
def refresh_accesos():
    """Recarga accesos y módulos desde BD en cada request."""
    if session.get('user_id') and session.get('rol_id'):
        rol_id = session['rol_id']
        session['accesos'] = cargar_accesos(rol_id)
        session['modulos'] = cargar_modulos(rol_id)

if __name__ == '__main__':
    # Railway inyecta PORT automáticamente
    port = int(os.environ.get('PORT', 8080))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    print(f"Starting server on port {port}")  # Debug log
    app.run(debug=debug, host='0.0.0.0', port=port)