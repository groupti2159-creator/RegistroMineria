import os
import re

filepath = r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\routes\desvios_ambientales.py"

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

def replacer(match):
    indent = match.group(1)
    body = match.group(2)
    
    # body contains full lines including their original indents.
    # We just want to add 4 spaces to each line.
    indented_body = '\n'.join('    ' + line if line.strip() else line for line in body.split('\n'))
    
    cur_assign = indent + '    ' + 'cur = mysql.connection.cursor()'
    
    replacement = (
        indent + "try:\n" +
        cur_assign + "\n" +
        indented_body + "\n" +
        indent + "finally:\n" +
        indent + "    if 'cur' in locals() and cur: cur.close()"
    )
    return replacement

pattern = re.compile(r"^([ \t]+)cur = mysql\.connection\.cursor\(\)\n(.*?)\n\1cur\.close\(\)", re.MULTILINE | re.DOTALL)

new_content = pattern.sub(replacer, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Patched all standalone cursors in desvios_ambientales.py")

# También gestion_residuos.py (aunque lo volvimos a checkout earlier, después le aplicamos el patch_routes.py para restaurar facturas. Ahora parchar cursores).
gr_filepath = r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\routes\gestion_residuos.py"
if os.path.exists(gr_filepath):
    with open(gr_filepath, 'r', encoding='utf-8') as f:
        gr_content = f.read()
    
    gr_new_content = pattern.sub(replacer, gr_content)
    with open(gr_filepath, 'w', encoding='utf-8') as f:
        f.write(gr_new_content)
    print("Patched all standalone cursors in gestion_residuos.py")
