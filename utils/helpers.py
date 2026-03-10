import uuid, os, hashlib
from werkzeug.utils import secure_filename
from contextlib import contextmanager
from utils.case_insensitive_dict import make_case_insensitive, make_list_case_insensitive

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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
