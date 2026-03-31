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

    # 1. Update the table column rendering
    # Look for <td>{{ r.factura or '—' }}</td>
    table_regex = re.compile(r"<td>\{\{\s*r\.factura\s*or\s*'—'\s*\}\}</td>")
    
    new_td = """<td>
            {% if r.factura %}
              {% if 'uploads/' in r.factura %}
                <a href="{{ '/static/' ~ r.factura.replace('static/', '') }}" target="_blank" style="color:var(--green);font-size:0.85rem;display:flex;align-items:center;gap:4px">
                  <i data-feather="file" style="width:14px;height:14px"></i> Ver Archivo
                </a>
              {% else %}
                {{ r.factura }}
              {% endif %}
            {% else %}
              —
            {% endif %}
          </td>"""
    
    content = table_regex.sub(new_td, content)

    # 2. Update the hidden inputs in the modal body, adding <input type="hidden" id="<prefix>-factura-old">
    modal_body_regex = re.compile(rf'<input type="hidden" id="{prefix}-id">')
    content = modal_body_regex.sub(f'<input type="hidden" id="{prefix}-id">\n      <input type="hidden" id="{prefix}-factura-old">', content)

    # 3. Update the factura file input field
    input_regex = re.compile(rf'<label class="date-label">Factura</label>\s*<input class="plant-input" type="text" id="{prefix}-factura".*?>')
    new_input = f'<label class="date-label">Factura (Imagen/PDF)</label>\n        <input class="plant-input" type="file" id="{prefix}-factura" accept="image/*,application/pdf" style="padding:.2rem">'
    content = input_regex.sub(new_input, content)

    # 4. In openModal javascript:
    old_open_1 = rf"\$\('{prefix}-factura'\)\.value\s*=\s*r \? r\.factura\s*:\s*'';"
    new_open_1 = f"$('{prefix}-factura').value = '';\n    $('{prefix}-factura-old').value = r ? r.factura : '';"
    content = re.sub(old_open_1, new_open_1, content)
    
    # Check alternative openModal spacing for compostaje/etc
    old_open_2 = rf"\$\('{prefix}-factura'\)\.value\s*=\s*r \? r\.factura\s*:\s*'';"
    # We already substituted this with regex, but maybe with spacing:
    # `$('com-factura').value    = r ? r.factura     : '';`
    content = re.sub(rf"\$\('{prefix}-factura'\)\.value\s*=\s*r\s*\?\s*r\.factura\s*:\s*'';", new_open_1, content)

    # 5. In guardar javascript:
    
    if prefix == 'com':
        guardar_regex = re.compile(r"const payload\s*=\s*\{.*?\};.*?const res\s*=\s*await fetch\(url, \{ method:'POST', headers:\{'Content-Type':'application/json'\}, body: JSON.stringify\(payload\) \}\);", re.DOTALL)
        
        new_guardar = """const formData = new FormData();
    formData.append('fecha', fecha);
    formData.append('supervisor', $('com-supervisor').value.trim());
    formData.append('tipo', $('com-tipo').value);
    formData.append('precio', $('com-precio').value);
    formData.append('guia', $('com-guia').value);
    formData.append('peso', $('com-peso').value);
    formData.append('obs', $('com-obs').value);
    formData.append('factura', $('com-factura-old').value);
    
    if ($('com-factura').files.length > 0) {
      formData.append('factura_file', $('com-factura').files[0]);
    }

    const url = id ? '/admin/residuos/comercializable/editar/' + id : '/admin/residuos/comercializable/guardar';
    const res  = await fetch(url, { method:'POST', body: formData });"""
        content = guardar_regex.sub(new_guardar, content)

    elif prefix == 'mat':
        guardar_regex = re.compile(r"const payload\s*=\s*\{.*?\};.*?const res\s*=\s*await fetch\(url, \{ method:'POST', headers:\{'Content-Type':'application/json'\}, body: JSON.stringify\(payload\) \}\);", re.DOTALL)
        
        new_guardar = """const formData = new FormData();
    formData.append('fecha', fecha);
    formData.append('supervisor', $('mat-supervisor').value.trim());
    formData.append('tipo', $('mat-tipo').value);
    formData.append('costo_viaje', $('mat-costo-viaje').value);
    formData.append('precio', $('mat-precio').value);
    formData.append('guia', $('mat-guia').value);
    formData.append('volumen', $('mat-volumen').value);
    formData.append('peso', $('mat-peso').value);
    formData.append('obs', $('mat-obs').value);
    formData.append('factura', $('mat-factura-old').value);
    
    if ($('mat-factura').files.length > 0) {
      formData.append('factura_file', $('mat-factura').files[0]);
    }

    const url = id ? '/admin/residuos/matpel/editar/' + id : '/admin/residuos/matpel/guardar';
    const res  = await fetch(url, { method:'POST', body: formData });"""
        content = guardar_regex.sub(new_guardar, content)
        
    elif prefix == 'comp':
        guardar_regex = re.compile(r"const payload\s*=\s*\{.*?\};.*?const res\s*=\s*await fetch\(url, \{ method:'POST', headers:\{'Content-Type':'application/json'\}, body: JSON.stringify\(payload\) \}\);", re.DOTALL)
        
        new_guardar = """const formData = new FormData();
    formData.append('fecha', fecha);
    formData.append('preparacion', $('comp-preparacion').value);
    formData.append('cosecha', $('comp-cosecha').value);
    formData.append('costo_viaje', $('comp-costo-viaje').value);
    formData.append('precio', $('comp-precio').value);
    formData.append('guia', $('comp-guia').value);
    formData.append('volumen', $('comp-volumen').value);
    formData.append('peso', $('comp-peso').value);
    formData.append('obs', $('comp-obs').value);
    formData.append('factura', $('comp-factura-old').value);
    
    if ($('comp-factura').files.length > 0) {
      formData.append('factura_file', $('comp-factura').files[0]);
    }

    const url = id ? '/admin/residuos/compostaje/editar/' + id : '/admin/residuos/compostaje/guardar';
    const res  = await fetch(url, { method:'POST', body: formData });"""
        content = guardar_regex.sub(new_guardar, content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Patched {path}")
