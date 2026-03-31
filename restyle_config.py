import os
import re

def update_usuarios():
    filepath = r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\templates\configuracion\usuarios.html"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_css = """<style>
/* ========== ESTILOS PARA GESTIÓN DE USUARIOS (Estandarizado) ========== */

#modalCrearUsuario .modal-box { max-width: 900px; }
#modalCrearUsuario .form-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
}
#modalCrearUsuario .form-section-title {
    margin: -1.5rem -1.5rem 1.5rem -1.5rem;
    padding: 1rem 1.5rem;
    background: var(--gray-50);
    border-bottom: 1px solid var(--border);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: .75rem;
    color: var(--text);
}
[data-theme="dark"] #modalCrearUsuario .form-section-title { background: var(--gray-800); }

#modalCrearUsuario .form-row { margin-bottom: 1.25rem; display: flex; gap: 1.25rem; }
#modalCrearUsuario .form-row:last-child { margin-bottom: 0; }
#modalCrearUsuario .form-group { flex: 1; display: flex; flex-direction: column; gap: .45rem; }

.search-bar, .filter-bar {
    background: var(--bg-card);
    padding: 1rem 1.25rem;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}

.users-table-container {
    background: var(--bg-card);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    overflow-x: auto;
}

.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
    padding: 1rem 1.25rem;
    text-align: left;
    font-size: .75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .05em;
    color: var(--text-muted);
    border-bottom: 2px solid var(--border);
    background: var(--gray-50);
}
[data-theme="dark"] .data-table th { background: var(--gray-800); }

.data-table td {
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
    color: var(--text);
}

.data-table tbody tr { transition: background-color 0.2s; }
.data-table tbody tr:hover { background: var(--gray-50); }
[data-theme="dark"] .data-table tbody tr:hover { background: var(--gray-800); }
.data-table tbody tr:last-child td { border-bottom: none; }

.user-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--gray-100), var(--gray-300));
    color: var(--text);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: .95rem;
    margin-right: 1.25rem;
    flex-shrink: 0;
    border: 2px solid var(--border);
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
[data-theme="dark"] .user-avatar { background: linear-gradient(135deg, var(--gray-700), var(--gray-800)); }

.user-info { display: flex; align-items: center; }
.user-name { font-weight: 600; font-size: .9rem; color: var(--text); margin-bottom: .2rem; }
.user-dni { font-size: .75rem; color: var(--text-muted); }

.role-badge {
    display: inline-flex;
    align-items: center;
    padding: .35rem .75rem;
    border-radius: 20px;
    font-size: .75rem;
    font-weight: 600;
    margin: 2px 4px 2px 0;
    white-space: nowrap;
    background: var(--bg-card);
    border: 1px solid var(--border);
    color: var(--text);
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.role-admin { border-left: 3px solid #ef4444; }
.role-supervisor { border-left: 3px solid #3b82f6; }
.role-trabajador { border-left: 3px solid #10b981; }

.status-badge {
    padding: .4rem .85rem;
    border-radius: 20px;
    font-size: .75rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: .5rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}
.status-active { color: #10b981; }
.status-inactive { color: #ef4444; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

.proyecto-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    border-radius: var(--radius-lg);
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    position: relative;
}
.proyecto-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.25rem;
    padding-bottom: 1rem;
    border-bottom: 1px dashed var(--border);
}
.proyecto-item-header strong { font-size: 1rem; font-weight: 700; color: var(--text); }

@media (max-width: 768px) {
    .filter-bar { flex-direction: column; align-items: stretch; }
}
</style>"""

    content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def update_roles():
    filepath = r"c:\Users\flans\Downloads\ecosupervisor_v2\ecosupervisor\templates\admin\roles.html"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_css = """<style>
/* ====================================================
   ESTILOS EXCLUSIVOS PARA GESTIÓN DE ROLES (Estandarizado)
==================================================== */

.roles-permissions-module {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.module-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 0.5rem;
}
.module-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0 0 .25rem 0;
    display: flex;
    align-items: center;
    gap: .5rem;
    color: var(--text);
}
.module-header p {
    font-size: .875rem;
    color: var(--text-muted);
    margin: 0;
}

.proyecto-selector {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 1rem 1.5rem;
    border-radius: var(--radius-lg);
    display: flex;
    align-items: center;
    gap: 1rem;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
}
.proyecto-selector label { font-size: .875rem; font-weight: 600; color: var(--text); display: flex; align-items: center; gap: .5rem; margin: 0; }
.proyecto-selector select { min-width: 250px; }

.roles-grid { display: flex; flex-direction: column; gap: 1.25rem; }

.role-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
}
.role-card:hover { box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }

.role-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.25rem 1.5rem;
    background: var(--gray-50);
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background 0.2s;
}
[data-theme="dark"] .role-header { background: var(--gray-800); }
.role-header:hover { background: var(--gray-100); }
[data-theme="dark"] .role-header:hover { background: var(--gray-700); }

.role-info { flex: 1; display: flex; align-items: center; gap: 1rem; }
.role-icon {
    width: 42px; height: 42px;
    background: var(--gray-200);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    color: var(--text);
}
[data-theme="dark"] .role-icon { background: var(--gray-700); }

.role-name { font-size: 1rem; font-weight: 700; color: var(--text); display: flex; align-items: center; gap: .75rem; }
.role-badge {
    font-size: .65rem; padding: .25rem .65rem;
    background: var(--gray-200); color: var(--text);
    border-radius: 12px; border: 1px solid var(--border);
}
[data-theme="dark"] .role-badge { background: var(--gray-700); }
.role-description { font-size: .85rem; color: var(--text-muted); margin-top: .25rem; }
.role-stats { display: flex; align-items: center; gap: .5rem; font-size: .8rem; color: var(--text-muted); margin-left: auto; margin-right: 1.5rem;}

.role-permissions {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease-out;
}
.role-permissions.open { max-height: 2000px; transition: max-height 0.4s ease-in; }

.permissions-header {
    padding: 1rem 1.5rem;
    background: var(--bg-card);
    border-bottom: 1px dashed var(--border);
    display: flex; justify-content: space-between; align-items: center;
}
.permissions-title { font-size: .85rem; font-weight: 700; color: var(--text); text-transform: uppercase; letter-spacing: 0.05em; display: flex; align-items: center; gap: .5rem; }

.select-all-btn {
    font-size: .8rem;
    font-weight: 600;
    color: var(--text-muted);
    background: var(--gray-100);
    border: 1px solid var(--border);
    padding: .35rem .85rem;
    border-radius: var(--radius);
    cursor: pointer;
    transition: all 0.2s;
}
[data-theme="dark"] .select-all-btn { background: var(--gray-800); }
.select-all-btn:hover { background: var(--gray-200); color: var(--text); }
[data-theme="dark"] .select-all-btn:hover { background: var(--gray-700); }

.categorias-tabs {
    display: flex; gap: .5rem; border-bottom: 1px solid var(--border);
    margin: 1rem 1.5rem 0 1.5rem; overflow-x: auto;
}
.tab-categoria {
    padding: .65rem 1rem; font-size: .85rem; font-weight: 600;
    color: var(--text-muted); cursor: pointer; border-bottom: 3px solid transparent;
    transition: all 0.2s; white-space: nowrap;
}
.tab-categoria:hover { color: var(--text); }
.tab-categoria.active { color: var(--text); border-bottom-color: currentColor; }

.permisos-container { display: none; padding: 1.5rem; }
.permisos-container.active { display: block; }
.permisos-horizontal { display: flex; flex-wrap: wrap; gap: .75rem; }

/* Switch-like chips */
.permiso-chip {
    display: inline-flex; align-items: center; gap: .75rem;
    padding: .6rem 1.25rem; background: var(--gray-50);
    border: 1px solid var(--border); border-radius: 8px;
    cursor: pointer; transition: all 0.2s; font-size: .85rem; font-weight: 500;
}
[data-theme="dark"] .permiso-chip { background: var(--gray-800); }
.permiso-chip:hover { border-color: var(--text-muted); }
.permiso-chip.selected {
    background: var(--bg-card);
    border-color: currentColor;
    color: currentColor;
    box-shadow: 0 0 0 1px currentColor;
}
.permiso-chip input[type="checkbox"] { width: 14px; height: 14px; cursor: pointer; }
.permiso-nombre { color: var(--text); }
.permiso-chip.selected .permiso-nombre { font-weight: 700; }

.message-toast {
    position: fixed; bottom: 20px; right: 20px;
    padding: 1rem 1.5rem; border-radius: var(--radius-lg);
    background: var(--bg-card); border: 1px solid var(--border);
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    display: flex; align-items: center; gap: .75rem; z-index: 1000; font-size: .875rem; font-weight: 600;
}
.message-toast.success { border-left: 4px solid #10b981; }
.message-toast.error { border-left: 4px solid #ef4444; }

@media (max-width: 768px) {
    .role-header, .proyecto-selector { flex-direction: column; align-items: stretch; gap: 1rem; }
    .role-stats { margin: .5rem 0 0 0; }
}
</style>"""

    content = re.sub(r'<style>.*?</style>', new_css, content, flags=re.DOTALL)
    # Reemplazar btn-red en roles.html que tal vez usaba colores raros o no era base
    content = content.replace('btn-red', 'btn-danger')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

update_usuarios()
update_roles()
print("Estilos actualizados!")
