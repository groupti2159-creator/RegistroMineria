#!/usr/bin/env python3
"""
Script para modularizar base.css completamente
Extrae secciones y crea archivos de componentes
"""

import os
import re

# Definir qué extraer y a dónde
EXTRACTIONS = {
    'layout/layout.css': {
        'start': '/* ── LAYOUT ──',
        'end': '/* ── SIDEBAR ──',
        'description': 'Layout principal'
    },
    'layout/topbar.css': {
        'start': '/* ── MAIN CONTENT ──',
        'end': '/* ── NOTIFICATIONS ──',
        'description': 'Top bar y main content'
    },
    'components/notifications.css': {
        'patterns': [
            r'\.ajax-notificacion.*?\n\}',
            r'\.toast-animate.*?\n\}',
            r'@keyframes (slideInRight|slideOutRight|toastSlideIn|toastSlideOut).*?\n\}',
            r'\.notif-(wrapper|btn|badge|panel|header|list|item|empty).*?\n\}',
        ],
        'description': 'Sistema de notificaciones'
    },
    'components/alerts.css': {
        'patterns': [
            r'\.alert.*?\n\}',
            r'\.info-banner.*?\n\}',
        ],
        'description': 'Alertas y banners'
    },
    'components/cards.css': {
        'patterns': [
            r'\.card(-title)?.*?\n\}',
            r'\.dashboard-(intro|grid).*?\n\}',
            r'\.section-(title|sub).*?\n\}',
            r'\.stats-grid.*?\n\}',
            r'\.stat-(card|label|value|desc|icon|blue|green|yellow|red).*?\n\}',
            r'\.quick-(actions|btn).*?\n\}',
            r'\.qa-(icon|title|sub).*?\n\}',
            r'\.activity-(list|item|dot|text).*?\n\}',
            r'\.dot-(info|success|warning|error).*?\n\}',
            r'\.empty-state.*?\n\}',
        ],
        'description': 'Cards y dashboard'
    },
}

def extract_section(content, start_marker, end_marker):
    """Extrae una sección entre dos marcadores"""
    start_idx = content.find(start_marker)
    if start_idx == -1:
        return None
    
    end_idx = content.find(end_marker, start_idx + len(start_marker))
    if end_idx == -1:
        end_idx = len(content)
    
    return content[start_idx:end_idx]

def extract_by_patterns(content, patterns):
    """Extrae contenido usando patrones regex"""
    extracted = []
    for pattern in patterns:
        matches = re.finditer(pattern, content, re.DOTALL | re.MULTILINE)
        for match in matches:
            extracted.append(match.group(0))
    return '\n\n'.join(extracted)

def main():
    base_css_path = 'RegistroMineria/static/css/base.css'
    
    with open(base_css_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🚀 Iniciando modularización completa de CSS...")
    print(f"📄 Archivo base: {base_css_path} ({len(content)} caracteres)")
    print()
    
    for target_file, config in EXTRACTIONS.items():
        target_path = f'RegistroMineria/static/css/{target_file}'
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        if 'start' in config and 'end' in config:
            extracted = extract_section(content, config['start'], config['end'])
        elif 'patterns' in config:
            extracted = extract_by_patterns(content, config['patterns'])
        else:
            continue
        
        if extracted:
            header = f"""/* =====================================================
   {config['description'].upper()}
===================================================== */

"""
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(header + extracted)
            
            print(f"✅ Creado: {target_file} ({len(extracted)} caracteres)")
        else:
            print(f"⚠️  No se encontró contenido para: {target_file}")
    
    print()
    print("✨ Modularización completada!")

if __name__ == '__main__':
    main()
