import uuid, os, hashlib
from werkzeug.utils import secure_filename
from contextlib import contextmanager
from utils.case_insensitive_dict import make_case_insensitive, make_list_case_insensitive

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'gif', 'webp', 'heic', 'heif', 'pdf'}

def gen_id():
    return str(uuid.uuid4())[:18]

def md5(text):
    return hashlib.md5(text.encode()).hexdigest()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, upload_folder, subfolder='evidencias'):
    if file and allowed_file(file.filename):
        ext      = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{gen_id()}.{ext}"
        folder   = os.path.join(upload_folder, subfolder)
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        file.save(filepath)
        size_kb  = os.path.getsize(filepath) // 1024
        rel_path = f"uploads/{subfolder}/{filename}"
        return rel_path, filename, size_kb
    return None, None, 0

def consume_results(cur):
    """Consume completamente todos los result sets pendientes de un cursor."""
    try:
        while True:
            try:
                cur.fetchall()
            except:
                pass
            if not cur.nextset():
                break
    except:
        pass

def sp_exec(cur, sp_name, params=()):
    """
    Llama a un stored procedure y consume TODOS los result sets.
    Retorna lista de filas del primer result set con datos.
    Los diccionarios son case-insensitive para compatibilidad Windows/Linux.
    """
    # Limpiar cualquier result set pendiente antes de ejecutar
    consume_results(cur)
    
    cur.callproc(sp_name, params)
    results = []
    first = True
    
    # Consumir todos los result sets
    while True:
        try:
            rows = cur.fetchall()
            if first and rows:
                results = make_list_case_insensitive(list(rows))
                first = False
        except Exception:
            pass
        
        # Intentar avanzar al siguiente result set
        if not cur.nextset():
            break
    
    return results

def sp_one(cur, sp_name, params=()):
    """Igual que sp_exec pero retorna solo la primera fila."""
    rows = sp_exec(cur, sp_name, params)
    return rows[0] if rows else None


# ── Decoradores y helpers compartidos para blueprints ────────────────────────

from functools import wraps
from flask import session, redirect, url_for, render_template

def admin_required(f):
    """
    DEPRECADO: Usar @login_required + @modulo_required en su lugar.
    Mantiene compatibilidad pero ahora permite acceso si el usuario tiene el módulo.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        # Ya no restringe solo a Administrador - cualquier usuario logueado puede acceder
        # La restricción real la hace @modulo_required
        return f(*args, **kwargs)
    return decorated

def login_required(f):
    """Verifica que el usuario esté logueado."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

def modulo_required(codigo):
    """Verifica que el usuario tenga acceso al modulo indicado."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            if codigo not in session.get('accesos', []):
                return render_template('auth/sin_acceso.html'), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

def delete_image_file(ruta):
    """Borra el archivo físico de una imagen dado su ruta relativa (ej: 'uploads/evidencias/xxx.jpg')."""
    if not ruta:
        return
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    filepath = os.path.normpath(os.path.join(base_dir, 'static', ruta))
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass

def get_notif_count():
    from extensions import mysql
    try:
        cur = mysql.connection.cursor()
        rows = sp_exec(cur, 'sp_contarnotificaciones', (session['usuario_rol'],))
        cur.close()
        return rows[0]['total'] if rows else 0
    except:
        return 0
