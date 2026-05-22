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

from routes.core.auth       import auth_bp
from routes.configuracion   import admin_bp
from routes.desvios_ambientales import da_bp
from routes.gestion_residuos    import gr_bp
from routes.compromisos         import compromisos_bp
from routes.meteorologia        import meteorologia_bp
from routes.gestion_aguas       import gestion_aguas_bp
from routes.core.supervisor import supervisor_bp
from routes.core.shared     import shared_bp
from routes.core.proyectos  import proyectos_bp
from routes.api             import api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp,        url_prefix='/admin')
app.register_blueprint(da_bp,           url_prefix='/admin')
app.register_blueprint(gr_bp,           url_prefix='/admin')
app.register_blueprint(compromisos_bp,  url_prefix='/admin')
app.register_blueprint(meteorologia_bp, url_prefix='/admin')
app.register_blueprint(gestion_aguas_bp, url_prefix='/admin')
app.register_blueprint(supervisor_bp,   url_prefix='/supervisor')
app.register_blueprint(shared_bp,       url_prefix='/api')
app.register_blueprint(api_bp,          url_prefix='/api')
app.register_blueprint(proyectos_bp,    url_prefix='/proyectos')

from flask import session, request
from utils.helpers import sp_exec
from datetime import datetime, timedelta

# Cache para evitar ejecutar el SP en cada request
_ultimo_update_estados = None
_intervalo_update = timedelta(minutes=5)  # Actualizar cada 5 minutos

# Nota: Los accesos y módulos se cargan una sola vez en login (set_session)
# No es necesario recargarlos en cada request

@app.before_request
def actualizar_estados_atrasados():
    """Actualiza estados atrasados automáticamente cada 5 minutos."""
    global _ultimo_update_estados
    
    # Solo ejecutar en requests HTML (no en static, API, etc.)
    if request.endpoint and 'static' not in request.endpoint:
        ahora = datetime.now()
        
        # Ejecutar si nunca se ha ejecutado o si pasaron más de 5 minutos
        if _ultimo_update_estados is None or (ahora - _ultimo_update_estados) > _intervalo_update:
            try:
                cur = mysql.connection.cursor()
                sp_exec(cur, 'sp_actualizarestadosatrasados')
                mysql.connection.commit()
                cur.close()
                _ultimo_update_estados = ahora
                print(f"[{ahora.strftime('%H:%M:%S')}] Estados atrasados actualizados")
            except Exception as e:
                print(f"[actualizar_estados_atrasados] error: {e}")
                # No interrumpir el request si falla

@app.after_request
def no_cache(response):
    """Evita que el browser cachee respuestas HTML."""
    if 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    # Railway inyecta PORT automáticamente
    port = int(os.environ.get('PORT', 8080))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    print(f"Starting server on port {port}")  # Debug log
    app.run(debug=debug, host='0.0.0.0', port=port)

    