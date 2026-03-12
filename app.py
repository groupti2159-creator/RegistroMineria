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
from routes.supervisor import supervisor_bp
from routes.shared     import shared_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp,       url_prefix='/admin')
app.register_blueprint(supervisor_bp,  url_prefix='/supervisor')
app.register_blueprint(shared_bp,      url_prefix='/api')

if __name__ == '__main__':
    # Railway inyecta PORT automáticamente
    port = int(os.environ.get('PORT', 8080))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    print(f"Starting server on port {port}")  # Debug log
    app.run(debug=debug, host='0.0.0.0', port=port)