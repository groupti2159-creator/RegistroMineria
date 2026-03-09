from flask import Flask
from dotenv import load_dotenv
import os
from extensions import mysql

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'ecosupervisor_2026')

app.config['MYSQL_HOST']        = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER']        = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD']    = os.getenv('MYSQL_PASSWORD', 'prototipo')
app.config['MYSQL_DB']          = os.getenv('MYSQL_DB', 'desvios_ambientales')
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
    app.run(debug=True, host='0.0.0.0', port=5000)
