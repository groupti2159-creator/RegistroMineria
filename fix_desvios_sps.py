from app import app
from extensions import mysql

def fix_sp_detalle():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Drop and recreate sp_detalleregistro — remove the invalid r.idubicacion column
        cur.execute("DROP PROCEDURE IF EXISTS sp_detalleregistro")
        
        sp_sql = """
        CREATE PROCEDURE sp_detalleregistro(IN p_idregistro INT)
        BEGIN
            SELECT 
                r.idregistro,
                r.codigo,
                r.fechainicio,
                r.fechaejecucion,
                r.descripcion,
                r.accion,
                r.notaslevantamiento,
                r.idareareportante,
                ar.areareportante,
                r.personalreportante,
                r.idarearesponsable,
                ares.arearesponsable,
                r.ubicacion,
                r.idriesgo,
                ri.riesgo,
                r.iddescripciontipo,
                dt.descripciontipo,
                r.riesgo_critico_id,
                r.idestado,
                e.estado,
                r.idusuariorolcreador,
                r.personalresponsable,
                r.personalresponsable_id,
                r.DniResponsable,
                r.cctaresponsable,
                ccta.areareportante as nombrecctaresponsable,
                r.archivado,
                r.fechaarchivado,
                r.idusuariorolarchivador,
                r.fechacreacion,
                r.fechaactualizacion,
                r.id_proyecto,
                r.idorigen,
                o.nombre as origen_nombre
            FROM tbl_registro r
            LEFT JOIN tbl_areareportante ar ON r.idareareportante = ar.idareareportante
            LEFT JOIN tbl_arearesponsable ares ON r.idarearesponsable = ares.idarearesponsable
            LEFT JOIN tbl_riesgo ri ON r.idriesgo = ri.idriesgo
            LEFT JOIN tbl_descripciontipo dt ON r.iddescripciontipo = dt.iddescripciontipo
            LEFT JOIN tbl_estado e ON r.idestado = e.idestado
            LEFT JOIN tbl_areareportante ccta ON r.cctaresponsable = ccta.idareareportante
            LEFT JOIN tbl_origen o ON r.idorigen = o.idorigen
            WHERE r.idregistro = p_idregistro;
        END
        """
        
        cur.execute(sp_sql)
        mysql.connection.commit()
        print("OK: sp_detalleregistro corregido (eliminada columna inexistente r.idubicacion)")
        cur.close()

def fix_sp_personal_area():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        cur.execute("DESCRIBE tbl_persona")
        cols = cur.fetchall()
        print("\ntbl_persona columns:")
        for c in cols:
            print(f"  {c['Field']} ({c['Type']})")
        
        has_area_resp = any(c['Field'].lower() == 'idarearesponsable' for c in cols)
        print(f"\n  tbl_persona tiene idarearesponsable: {has_area_resp}")
        
        cur.close()

if __name__ == '__main__':
    print("="*60)
    print("CORRIGIENDO SPs de Desvios Ambientales")
    print("="*60)
    fix_sp_detalle()
    fix_sp_personal_area()
    print("\nCOMPLETADO")
