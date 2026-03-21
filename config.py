import os

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ecosupervisor_2026'

    # Credenciales Railway (fallback si no hay variables de entorno)
    _DB_HOST     = 'centerbeam.proxy.rlwy.net'
    _DB_PORT     = '12842'
    _DB_USER     = 'root'
    _DB_PASSWORD = 'xjIkFDMLeGlztTsaAlDIjEQpVKiObtPj'
    _DB_NAME     = 'desvios_ambientales'

    MYSQL_HOST = (
        os.environ.get('DB_HOST') or
        os.environ.get('MYSQLHOST') or
        os.environ.get('MYSQL_HOST') or
        _DB_HOST
    )

    MYSQL_USER = (
        os.environ.get('DB_USER') or
        os.environ.get('MYSQLUSER') or
        os.environ.get('MYSQL_USER') or
        _DB_USER
    )

    MYSQL_PASSWORD = (
        os.environ.get('DB_PASSWORD') or
        os.environ.get('MYSQLPASSWORD') or
        os.environ.get('MYSQL_PASSWORD') or
        _DB_PASSWORD
    )

    MYSQL_DB = (
        os.environ.get('DB_NAME') or
        os.environ.get('MYSQLDATABASE') or
        os.environ.get('MYSQL_DB') or
        _DB_NAME
    )

    MYSQL_PORT = int(
        os.environ.get('DB_PORT') or
        os.environ.get('MYSQLPORT') or
        os.environ.get('MYSQL_PORT') or
        _DB_PORT
    )

    MYSQL_CURSORCLASS = 'DictCursor'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    @staticmethod
    def print_config():
        print("=" * 50)
        print("CONFIGURACIÓN MYSQL")
        print(f"Host: {Config.MYSQL_HOST}")
        print(f"User: {Config.MYSQL_USER}")
        print(f"Database: {Config.MYSQL_DB}")
        print(f"Port: {Config.MYSQL_PORT}")
        print(f"Password configurado: {'Sí' if Config.MYSQL_PASSWORD else 'No'}")
        print("=" * 50)
