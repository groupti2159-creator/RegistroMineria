# ============================================================================
# API — Cambiar Contraseña
# ============================================================================
from flask import request, jsonify, session
from extensions import mysql
from routes.api import api_bp
import hashlib


@api_bp.route('/cambiar-contrasena', methods=['POST'])
def cambiar_contrasena():
    """Endpoint para cambiar la contraseña del usuario actual"""
    
    # Verificar que el usuario esté autenticado
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'No autenticado'}), 401
    
    try:
        data = request.get_json()
        contrasena_actual = data.get('contrasena_actual', '').strip()
        contrasena_nueva = data.get('contrasena_nueva', '').strip()
        
        if not contrasena_actual or not contrasena_nueva:
            return jsonify({'success': False, 'error': 'Contraseña actual y nueva son requeridas'}), 400
        
        user_id = session['user_id']
        
        # Obtener la contraseña actual del usuario
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT contrasena FROM tbl_usuario WHERE idusuario = %s
        """, (user_id,))
        
        result = cur.fetchone()
        cur.close()
        
        if not result:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404
        
        # Verificar que la contraseña actual sea correcta
        contrasena_actual_hash = hashlib.md5(contrasena_actual.encode()).hexdigest()
        if result['contrasena'] != contrasena_actual_hash:
            return jsonify({'success': False, 'error': 'Contraseña actual incorrecta'}), 401
        
        # Actualizar la contraseña
        contrasena_nueva_hash = hashlib.md5(contrasena_nueva.encode()).hexdigest()
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE tbl_usuario SET contrasena = %s WHERE idusuario = %s
        """, (contrasena_nueva_hash, user_id))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Contraseña cambiada exitosamente'}), 200
        
    except Exception as e:
        print(f"[cambiar_contrasena] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error interno del servidor'}), 500
