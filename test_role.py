import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import app
from extensions import mysql

def test_role():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # 1. Crear el Rol 'Auditor de Prueba'
        print('1. Buscando o creando Rol Auditor...')
        cur.execute("SELECT idroles FROM tbl_roles WHERE nombrerol = 'Auditor de Prueba'")
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO tbl_roles (nombrerol, descripcion) VALUES ('Auditor de Prueba', 'Rol restringido para pruebas')")
            role_id = cur.lastrowid
        else:
            role_id = row['idroles']
        
        print(f"ID del nuevo Rol: {role_id}")

        # 2. Limpiar permisos previos si existen
        cur.execute("DELETE FROM tbl_proyecto_rol_modulo WHERE idroles = %s AND idproyecto = 1", (role_id,))

        # 3. Buscar módulos específicos (Dashboard, Estadisticas, Desvios)
        cur.execute("SELECT idmodulo, nombre FROM tbl_modulo WHERE codigo IN ('DASHBOARD', 'ESTADISTICAS', 'DESVIOS_AMB')")
        modulos = cur.fetchall()
        
        print(f"Asignando {len(modulos)} módulos al Proyecto 1...")
        for mod in modulos:
            m_id = mod['idmodulo']
            # CORREGIDO: 3 placeholders para 3 argumentos
            cur.execute("INSERT INTO tbl_proyecto_rol_modulo (idproyecto, idroles, idmodulo) VALUES (%s, %s, %s)", (1, role_id, m_id))

        mysql.connection.commit()
        print("\n[¡PRUEBA FINALIZADA CON ÉXITO!]")
        print(f"Resultado: El rol 'Auditor de Prueba' (ID {role_id}) ya tiene permisos asignados.")
        cur.close()

if __name__ == '__main__':
    test_role()
