from extensions import mysql
from app import app
from datetime import datetime

with app.app_context():
    try:
        cur = mysql.connection.cursor()
        
        # Obtener IDs necesarios
        cur.execute("SELECT idareareportante FROM tbl_areareportante LIMIT 1")
        area_rep = cur.fetchone()['idareareportante']
        
        cur.execute("SELECT idarearesponsable FROM tbl_arearesponsable LIMIT 1")
        area_res = cur.fetchone()['idarearesponsable']
        
        cur.execute("SELECT id FROM tbl_persona LIMIT 1")
        persona = cur.fetchone()['id']
        
        cur.execute("SELECT idriesgo FROM tbl_riesgo LIMIT 1")
        riesgo = cur.fetchone()['idriesgo']
        
        cur.execute("SELECT iddescripciontipo FROM tbl_descripciontipo LIMIT 1")
        tipo = cur.fetchone()['iddescripciontipo']
        
        cur.execute("SELECT id FROM tbl_riesgos_criticos LIMIT 1")
        riesgo_critico = cur.fetchone()['id']
        
        cur.execute("SELECT idestado FROM tbl_estado WHERE estado = 'Pendiente' LIMIT 1")
        estado = cur.fetchone()['idestado']
        
        cur.execute("SELECT idusuariorol FROM tbl_usuariorol LIMIT 1")
        usuario = cur.fetchone()['idusuariorol']
        
        print("Insertando registro de prueba...")
        cur.execute("""
            INSERT INTO tbl_registro (
                Codigo, FechaInicio, FechaEjecucion, Descripcion, Accion,
                idAreaReportante, personalreportante, idAreaResponsable, ubicacion, IdRiesgo,
                IdDescripcionTipo, riesgo_critico_id, idEstado, IdUsuarioRolCreador,
                personalresponsable_id, FechaCreacion
            ) VALUES (
                'TEST-001', NOW(), NOW(), 'Registro de prueba', 'Acción de prueba',
                %s, %s, %s, 'Ubicación de prueba', %s,
                %s, %s, %s, %s,
                %s, NOW()
            )
        """, (area_rep, persona, area_res, riesgo, tipo, riesgo_critico, estado, usuario, persona))
        
        mysql.connection.commit()
        
        # Verificar
        cur.execute("SELECT COUNT(*) as total FROM tbl_registro")
        total = cur.fetchone()['total']
        print(f"\n✅ Registro insertado. Total: {total}")
        
        # Probar el SP de listar
        print("\n=== PROBANDO SP_ListarRegistros ===")
        cur.callproc('sp_listarregistros', (None,))
        for result in cur.stored_results():
            registros = result.fetchall()
            print(f"Registros encontrados: {len(registros)}")
            if registros:
                print(f"Primer registro: {registros[0].get('Codigo', 'N/A')}")
        
        cur.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
