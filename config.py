import os

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ecosupervisor_2026'
    
    # MySQL Configuration - Railway compatible
    # Intenta múltiples nombres de variables:
    # 1. DB_HOST, DB_USER, etc. (Railway custom)
    # 2. MYSQLHOST, MYSQLUSER, etc. (Railway MySQL service)
    # 3. MYSQL_HOST, MYSQL_USER, etc. (Variables personalizadas)
    # 4. Valores por defecto para desarrollo local
    
    MYSQL_HOST = (
        os.environ.get('DB_HOST') or
        os.environ.get('MYSQLHOST') or 
        os.environ.get('MYSQL_HOST') or 
        'localhost'
    )
    
    MYSQL_USER = (
        os.environ.get('DB_USER') or
        os.environ.get('MYSQLUSER') or 
        os.environ.get('MYSQL_USER') or 
        'root'
    )
    
    MYSQL_PASSWORD = (
        os.environ.get('DB_PASSWORD') or
        os.environ.get('MYSQLPASSWORD') or 
        os.environ.get('MYSQL_PASSWORD') or 
        ''
    )
    
    MYSQL_DB = (
        os.environ.get('DB_NAME') or
        os.environ.get('MYSQLDATABASE') or 
        os.environ.get('MYSQL_DB') or 
        'desvios_ambientales'
    )
    
    MYSQL_PORT = int(
        os.environ.get('DB_PORT') or
        os.environ.get('MYSQLPORT') or 
        os.environ.get('MYSQL_PORT') or 
        3306
    )
    
    MYSQL_CURSORCLASS = 'DictCursor'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    @staticmethod
    def print_config():
        """Imprime la configuración actual (sin password)"""
        print("=" * 50)
        print("CONFIGURACIÓN MYSQL")
        print("=" * 50)
        print(f"Host: {Config.MYSQL_HOST}")
        print(f"User: {Config.MYSQL_USER}")
        print(f"Database: {Config.MYSQL_DB}")
        print(f"Port: {Config.MYSQL_PORT}")
        print(f"Password configurado: {'Sí' if Config.MYSQL_PASSWORD else 'No'}")
        print("=" * 50)
        
        # Imprimir todas las variables de entorno relevantes
        print("\nVariables de entorno encontradas:")
        for prefix in ['DB_', 'MYSQL']:
            for key, value in os.environ.items():
                if key.startswith(prefix):
                    # Ocultar password
                    if 'PASSWORD' in key or 'PASS' in key:
                        print(f"  {key}: ***")
                    else:
                        print(f"  {key}: {value}")
        print("=" * 50)
