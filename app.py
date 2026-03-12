from flask import Flask
from dotenv import load_dotenv
import os
from extensions import mysql

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'ecosupervisor_2026')

# Configuración de MySQL - Compatible con Railway
# Railway puede proporcionar MYSQLHOST, MYSQLUSER, etc. o MYSQL_HOST, MYSQL_USER, etc.
mysql_host = os.getenv('MYSQLHOST') or os.getenv('MYSQL_HOST', 'localhost')
mysql_user = os.getenv('MYSQLUSER') or os.getenv('MYSQL_USER', 'root')
mysql_password = os.getenv('MYSQLPASSWORD') or os.getenv('MYSQL_PASSWORD', '')
mysql_db = os.getenv('MYSQLDATABASE') or os.getenv('MYSQL_DB', 'desvios_ambientales')
mysql_port = int(os.getenv('MYSQLPORT') or os.getenv('MYSQL_PORT', 3306))

# Debug: Imprimir configuración (sin password)
print(f"=== CONFIGURACIÓN MYSQL ===")
print(f"Host: {mysql_host}")
print(f"User: {mysql_user}")
print(f"DB: {mysql_db}")
print(f"Port: {mysql_port}")
print(f"===========================")

app.config['MYSQL_HOST']        = mysql_host
app.config['MYSQL_USER']        = mysql_user
app.config['MYSQL_PASSWORD']    = mysql_password
app.config['MYSQL_DB']          = mysql_db
app.config['MYSQL_PORT']        = mysql_port
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER']     = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH']= 16 * 1024 * 1024

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