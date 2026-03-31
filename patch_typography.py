import re

files = [
    r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\templates\gestion_residuos\comercializable.html",
    r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\templates\gestion_residuos\matpel.html",
    r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\templates\gestion_residuos\compostaje.html",
]

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Eliminar el bloque de estilo embebido que alinea a la derecha
    # .plant-input, .date-input { ... text-align: right; ... }
    # Busquemos usando regex no muy estricta:
    style_regex = re.compile(r'\.plant-input,\s*\.date-input\s*\{[^}]*\}', re.DOTALL)
    content = style_regex.sub('', content)

    # También puede que .date-label esté definido
    label_style_regex = re.compile(r'\.date-label\s*\{[^}]*\}', re.DOTALL)
    content = label_style_regex.sub('', content)

    # 2. Reemplazar las clases en el HTML
    content = content.replace('class="date-label"', 'class="form-label"')
    
    # Para los select, plant-input -> form-select
    content = re.sub(r'<select class="plant-input"', r'<select class="form-select"', content)
    # Por si acaso hay espacios:
    content = re.sub(r'<select([^>]+)class="plant-input"', r'<select\1class="form-select"', content)

    # Para los inputs normales plant-input -> form-input
    content = content.replace('class="plant-input"', 'class="form-input"')
    
    # Para el input de tipo archivo modificado antes, maybe form-input? We shouldn't change the "file-input" class of actual inputs if we added one, but earlier we generated `<div class="file-upload-area">...` without class on file form (wait, `id="com-factura"` has no class in my previous patch). 
    
    # date-input -> form-input
    content = content.replace('class="date-input"', 'class="form-input"')

    # Optional: we can change the div wrappers
    # <div style="display:flex;flex-direction:column;gap:.35rem"> -> <div class="form-group">
    # Wait, the spacing in form-group is usually handled by main.css. 
    # Let's replace that inline style with pure class="form-group"
    content = content.replace('style="display:flex;flex-direction:column;gap:.35rem"', 'class="form-group"')
    # Si hay algo como grid-column:1/-1 además de esto:
    content = content.replace('style="display:flex;flex-direction:column;gap:.35rem;grid-column:1/-1"', 'class="form-group" style="grid-column:1/-1"')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Typography patched for {path}")
