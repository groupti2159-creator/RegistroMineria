"""
Script para depurar qué hay en la sesión
Agregar esto temporalmente a una ruta para ver qué contiene session
"""

# Agregar esto en routes/desvios_ambientales/dashboard.py temporalmente:

"""
@da_bp.route('/debug_session')
@admin_required
def debug_session():
    from flask import session, jsonify
    return jsonify({
        'modulos': session.get('modulos', []),
        'accesos': session.get('accesos', []),
        'user_id': session.get('user_id'),
        'rol': session.get('rol'),
        'proyecto_id': session.get('proyecto_id')
    })
"""

print("Agrega esta ruta temporalmente a dashboard.py para depurar")
