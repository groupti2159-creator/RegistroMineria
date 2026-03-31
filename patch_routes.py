import re
import sys

filepath = r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\routes\gestion_residuos.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
if 'save_image' not in content:
    content = content.replace(
        "from utils.helpers import admin_required, modulo_required, get_notif_count, sp_exec, sp_one",
        "from utils.helpers import admin_required, modulo_required, get_notif_count, sp_exec, sp_one, save_image, delete_image_file\nimport os"
    )

# COMERCIALIZABLE GUARDAR
repl_comercializable_guardar = """@gr_bp.route('/residuos/comercializable/guardar', methods=['POST'])
@admin_required
def comercializable_guardar():
    d = request.form
    factura = d.get('factura')
    if 'factura_file' in request.files and request.files['factura_file'].filename:
        ruta, nombre, kb = save_image(request.files['factura_file'], 'static/uploads', 'facturas_residuos')
        if ruta: factura = ruta
    try:
        cur = mysql.connection.cursor()
        row = sp_one(cur, 'SP_Comercializable_Guardar', (
            d.get('fecha'), d.get('supervisor'), d.get('tipo'),
            float(d.get('precio')) if d.get('precio') else None, d.get('guia'), factura,
            float(d.get('peso')) if d.get('peso') else None, d.get('obs'), session.get('user_id')
        ))"""

# COMERCIALIZABLE EDITAR
repl_comercializable_editar = """@gr_bp.route('/residuos/comercializable/editar/<int:rid>', methods=['POST'])
@admin_required
def comercializable_editar(rid):
    d = request.form
    factura = d.get('factura')
    if 'factura_file' in request.files and request.files['factura_file'].filename:
        cur = mysql.connection.cursor()
        cur.execute("SELECT factura FROM tbl_comercializable WHERE id = %s", (rid,))
        old = cur.fetchone()
        if old and isinstance(old, dict) and old.get('factura'): delete_image_file(old.get('factura'))
        elif old and isinstance(old, tuple) and old[0]: delete_image_file(old[0])
        cur.close()
        ruta, nombre, kb = save_image(request.files['factura_file'], 'static/uploads', 'facturas_residuos')
        if ruta: factura = ruta
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'SP_Comercializable_Editar', (
            rid, d.get('fecha'), d.get('supervisor'), d.get('tipo'),
            float(d.get('precio')) if d.get('precio') else None, d.get('guia'), factura,
            float(d.get('peso')) if d.get('peso') else None, d.get('obs')
        ))"""

# COMERCIALIZABLE ELIMINAR
repl_comercializable_eliminar = """@gr_bp.route('/residuos/comercializable/eliminar/<int:rid>', methods=['POST'])
@admin_required
def comercializable_eliminar(rid):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT factura FROM tbl_comercializable WHERE id = %s", (rid,))
        old = cur.fetchone()
        if old and isinstance(old, dict) and old.get('factura'): delete_image_file(old.get('factura'))
        elif old and isinstance(old, tuple) and old[0]: delete_image_file(old[0])
        cur.close()
        
        cur = mysql.connection.cursor()
        sp_exec(cur, 'SP_Comercializable_Eliminar', (rid,))"""

# MATPEL GUARDAR
repl_matpel_guardar = """@gr_bp.route('/residuos/matpel/guardar', methods=['POST'])
@admin_required
def matpel_guardar():
    d = request.form
    factura = d.get('factura')
    if 'factura_file' in request.files and request.files['factura_file'].filename:
        ruta, nombre, kb = save_image(request.files['factura_file'], 'static/uploads', 'facturas_residuos')
        if ruta: factura = ruta
    try:
        cur = mysql.connection.cursor()
        row = sp_one(cur, 'SP_Matpel_Guardar', (
            d.get('fecha'), d.get('supervisor'), d.get('tipo'),
            float(d.get('costo_viaje')) if d.get('costo_viaje') else None, float(d.get('precio')) if d.get('precio') else None,
            d.get('guia'), factura,
            float(d.get('volumen')) if d.get('volumen') else None, float(d.get('peso')) if d.get('peso') else None,
            d.get('obs'), session.get('user_id')
        ))"""

# MATPEL EDITAR
repl_matpel_editar = """@gr_bp.route('/residuos/matpel/editar/<int:rid>', methods=['POST'])
@admin_required
def matpel_editar(rid):
    d = request.form
    factura = d.get('factura')
    if 'factura_file' in request.files and request.files['factura_file'].filename:
        cur = mysql.connection.cursor()
        cur.execute("SELECT factura FROM tbl_matpel WHERE id = %s", (rid,))
        old = cur.fetchone()
        if old and isinstance(old, dict) and old.get('factura'): delete_image_file(old.get('factura'))
        elif old and isinstance(old, tuple) and old[0]: delete_image_file(old[0])
        cur.close()
        ruta, nombre, kb = save_image(request.files['factura_file'], 'static/uploads', 'facturas_residuos')
        if ruta: factura = ruta
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'SP_Matpel_Editar', (
            rid, d.get('fecha'), d.get('supervisor'), d.get('tipo'),
            float(d.get('costo_viaje')) if d.get('costo_viaje') else None, float(d.get('precio')) if d.get('precio') else None,
            d.get('guia'), factura,
            float(d.get('volumen')) if d.get('volumen') else None, float(d.get('peso')) if d.get('peso') else None,
            d.get('obs')
        ))"""

# MATPEL ELIMINAR
repl_matpel_eliminar = """@gr_bp.route('/residuos/matpel/eliminar/<int:rid>', methods=['POST'])
@admin_required
def matpel_eliminar(rid):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT factura FROM tbl_matpel WHERE id = %s", (rid,))
        old = cur.fetchone()
        if old and isinstance(old, dict) and old.get('factura'): delete_image_file(old.get('factura'))
        elif old and isinstance(old, tuple) and old[0]: delete_image_file(old[0])
        cur.close()

        cur = mysql.connection.cursor()
        sp_exec(cur, 'SP_Matpel_Eliminar', (rid,))"""

# COMPOSTAJE GUARDAR
repl_compostaje_guardar = """@gr_bp.route('/residuos/compostaje/guardar', methods=['POST'])
@admin_required
def compostaje_guardar():
    d = request.form
    factura = d.get('factura')
    if 'factura_file' in request.files and request.files['factura_file'].filename:
        ruta, nombre, kb = save_image(request.files['factura_file'], 'static/uploads', 'facturas_residuos')
        if ruta: factura = ruta
    try:
        cur = mysql.connection.cursor()
        row = sp_one(cur, 'SP_Compostaje_Guardar', (
            d.get('fecha'),
            float(d.get('preparacion')) if d.get('preparacion') else None, float(d.get('cosecha')) if d.get('cosecha') else None,
            float(d.get('costo_viaje')) if d.get('costo_viaje') else None, float(d.get('precio')) if d.get('precio') else None,
            d.get('guia'), factura,
            float(d.get('volumen')) if d.get('volumen') else None, float(d.get('peso')) if d.get('peso') else None,
            d.get('obs'), session.get('user_id')
        ))"""

# COMPOSTAJE EDITAR
repl_compostaje_editar = """@gr_bp.route('/residuos/compostaje/editar/<int:rid>', methods=['POST'])
@admin_required
def compostaje_editar(rid):
    d = request.form
    factura = d.get('factura')
    if 'factura_file' in request.files and request.files['factura_file'].filename:
        cur = mysql.connection.cursor()
        cur.execute("SELECT factura FROM tbl_compostaje WHERE id = %s", (rid,))
        old = cur.fetchone()
        if old and isinstance(old, dict) and old.get('factura'): delete_image_file(old.get('factura'))
        elif old and isinstance(old, tuple) and old[0]: delete_image_file(old[0])
        cur.close()
        ruta, nombre, kb = save_image(request.files['factura_file'], 'static/uploads', 'facturas_residuos')
        if ruta: factura = ruta
    try:
        cur = mysql.connection.cursor()
        sp_exec(cur, 'SP_Compostaje_Editar', (
            rid, d.get('fecha'),
            float(d.get('preparacion')) if d.get('preparacion') else None, float(d.get('cosecha')) if d.get('cosecha') else None,
            float(d.get('costo_viaje')) if d.get('costo_viaje') else None, float(d.get('precio')) if d.get('precio') else None,
            d.get('guia'), factura,
            float(d.get('volumen')) if d.get('volumen') else None, float(d.get('peso')) if d.get('peso') else None,
            d.get('obs')
        ))"""

# COMPOSTAJE ELIMINAR
repl_compostaje_eliminar = """@gr_bp.route('/residuos/compostaje/eliminar/<int:rid>', methods=['POST'])
@admin_required
def compostaje_eliminar(rid):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT factura FROM tbl_compostaje WHERE id = %s", (rid,))
        old = cur.fetchone()
        if old and isinstance(old, dict) and old.get('factura'): delete_image_file(old.get('factura'))
        elif old and isinstance(old, tuple) and old[0]: delete_image_file(old[0])
        cur.close()

        cur = mysql.connection.cursor()
        sp_exec(cur, 'SP_Compostaje_Eliminar', (rid,))"""

# Aplicar regex replacements

content = re.sub(
    r"@gr_bp\.route\('/residuos/comercializable/guardar', methods=\['POST'\]\).*?d\.get\('obs'\), session\.get\('user_id'\)\n        \)\)",
    repl_comercializable_guardar, content, flags=re.DOTALL
)

content = re.sub(
    r"@gr_bp\.route\('/residuos/comercializable/editar/<int:rid>', methods=\['POST'\]\).*?d\.get\('obs'\)\n        \)\)",
    repl_comercializable_editar, content, flags=re.DOTALL
)

content = re.sub(
    r"@gr_bp\.route\('/residuos/comercializable/eliminar/<int:rid>', methods=\['POST'\]\).*?sp_exec\(cur, 'SP_Comercializable_Eliminar', \(rid,\)\)",
    repl_comercializable_eliminar, content, flags=re.DOTALL
)


content = re.sub(
    r"@gr_bp\.route\('/residuos/matpel/guardar', methods=\['POST'\]\).*?d\.get\('obs'\), session\.get\('user_id'\)\n        \)\)",
    repl_matpel_guardar, content, flags=re.DOTALL
)

content = re.sub(
    r"@gr_bp\.route\('/residuos/matpel/editar/<int:rid>', methods=\['POST'\]\).*?d\.get\('obs'\)\n        \)\)",
    repl_matpel_editar, content, flags=re.DOTALL
)

content = re.sub(
    r"@gr_bp\.route\('/residuos/matpel/eliminar/<int:rid>', methods=\['POST'\]\).*?sp_exec\(cur, 'SP_Matpel_Eliminar', \(rid,\)\)",
    repl_matpel_eliminar, content, flags=re.DOTALL
)


content = re.sub(
    r"@gr_bp\.route\('/residuos/compostaje/guardar', methods=\['POST'\]\).*?d\.get\('obs'\), session\.get\('user_id'\)\n        \)\)",
    repl_compostaje_guardar, content, flags=re.DOTALL
)

content = re.sub(
    r"@gr_bp\.route\('/residuos/compostaje/editar/<int:rid>', methods=\['POST'\]\).*?d\.get\('obs'\)\n        \)\)",
    repl_compostaje_editar, content, flags=re.DOTALL
)

content = re.sub(
    r"@gr_bp\.route\('/residuos/compostaje/eliminar/<int:rid>', methods=\['POST'\]\).*?sp_exec\(cur, 'SP_Compostaje_Eliminar', \(rid,\)\)",
    repl_compostaje_eliminar, content, flags=re.DOTALL
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to routes/gestion_residuos.py")
