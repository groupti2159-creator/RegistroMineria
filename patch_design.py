import re

files = [
    {
        "path": r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\templates\gestion_residuos\comercializable.html",
        "prefix": "com"
    },
    {
        "path": r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\templates\gestion_residuos\matpel.html",
        "prefix": "mat"
    },
    {
        "path": r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\templates\gestion_residuos\compostaje.html",
        "prefix": "comp"
    }
]

for file_info in files:
    path = file_info["path"]
    prefix = file_info["prefix"]
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the HTML structure of the file input
    # Look for:
    # <label class="date-label">Factura (Imagen/PDF)</label>
    # <input class="plant-input" type="file" id="com-factura" accept="image/*,application/pdf" style="padding:.2rem">
    
    old_input_html = f'<label class="date-label">Factura (Imagen/PDF)</label>\n        <input class="plant-input" type="file" id="{prefix}-factura" accept="image/*,application/pdf" style="padding:.2rem">'
    
    new_input_html = f"""<label class="date-label">Factura (Imagen/PDF)</label>
        <div class="file-upload-area" style="margin-top:.2rem">
          <input type="file" id="{prefix}-factura" accept="image/*,application/pdf" style="display:none">
          <label for="{prefix}-factura" style="display:flex;align-items:center;gap:.5rem;cursor:pointer;padding:.4rem .6rem;border:1px dashed var(--border);border-radius:6px;background:var(--bg-card);transition:border-color 0.2s">
            <span class="btn" style="padding:.2rem .5rem;font-size:.75rem;background:var(--bg-hover);color:var(--text);border:1px solid var(--border);border-radius:4px"><i data-feather="upload" style="width:12px;height:12px"></i> Buscar</span>
            <span id="{prefix}-factura-name" style="font-size:.8rem;color:var(--text-muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:180px">Sin archivo seleccionado</span>
          </label>
        </div>
        <div id="{prefix}-factura-preview" style="display:none;margin-top:.4rem">
           <img id="{prefix}-factura-img" style="max-width:100%;max-height:140px;border-radius:4px;border:1px solid var(--border);object-fit:cover">
           <div id="{prefix}-factura-pdf" style="display:none;font-size:.8rem;color:var(--green);align-items:center;gap:4px">
             <i data-feather="file-text" style="width:14px;height:14px"></i> Documento PDF seleccionado
           </div>
        </div>
        <div id="{prefix}-factura-old-link" style="display:none;margin-top:.3rem;font-size:.8rem">
        </div>"""

    content = content.replace(old_input_html, new_input_html)

    # 2. In JavaScript, add the event listener for the file input change
    # We can inject this right before: `$('btn-open-comp').addEventListener('click'...` or similar initialization block
    
    js_listener = f"""  $('{prefix}-factura').addEventListener('change', function(e) {{
    const file = e.target.files[0];
    if (file) {{
      $('{prefix}-factura-name').textContent = file.name;
      $('{prefix}-factura-preview').style.display = 'block';
      if (file.type.startsWith('image/')) {{
        const reader = new FileReader();
        reader.onload = ev => {{ 
          $('{prefix}-factura-img').src = ev.target.result; 
          $('{prefix}-factura-img').style.display = 'block'; 
          $('{prefix}-factura-pdf').style.display = 'none'; 
        }};
        reader.readAsDataURL(file);
      }} else {{
        $('{prefix}-factura-img').style.display = 'none';
        $('{prefix}-factura-pdf').style.display = 'flex';
      }}
    }} else {{
      $('{prefix}-factura-name').textContent = 'Sin archivo seleccionado';
      $('{prefix}-factura-preview').style.display = 'none';
    }}
  }});\n\n  $"""
    
    content = content.replace(f"  $('btn-open-{prefix}')", js_listener + f"('btn-open-{prefix}')")


    # 3. Modify openModal logic
    # Look for: $('com-factura').value = '';\n    $('com-factura-old').value = r ? r.factura : '';
    
    old_open_logic = f"$('{prefix}-factura').value = '';\n    $('{prefix}-factura-old').value = r ? r.factura : '';"
    new_open_logic = f"""$('{prefix}-factura').value = '';
    $('{prefix}-factura-name').textContent = 'Sin archivo seleccionado';
    $('{prefix}-factura-preview').style.display = 'none';
    $('{prefix}-factura-old').value = r ? r.factura : '';
    
    if (r && r.factura) {{
       $('{prefix}-factura-old-link').style.display = 'block';
       const href = r.factura.includes('uploads') ? '/static/' + r.factura.replace('static/', '') : '#';
       $('{prefix}-factura-old-link').innerHTML = '<span style="color:var(--text-muted)">Archivo actual: </span><a href="' + href + '" target="_blank" style="color:var(--green);text-decoration:none"><i data-feather="external-link" style="width:12px;height:12px;margin-right:2px"></i>Ver documento</a>';
    }} else {{
       $('{prefix}-factura-old-link').style.display = 'none';
    }}"""
    
    content = content.replace(old_open_logic, new_open_logic)

    # 4. As feather icons are added natively in innerHTML, we should call feather.replace() inside openModal
    # Right after we do the html injection, we can hook it at the end of openModal. 
    # Look for: $('modal-com-overlay').classList.add('open');
    
    old_open_end = f"$('modal-{prefix}-overlay').classList.add('open');"
    new_open_end = f"$('modal-{prefix}-overlay').classList.add('open');\n    if (window.feather) feather.replace();"
    content = content.replace(old_open_end, new_open_end)


    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Design patched for {path}")
