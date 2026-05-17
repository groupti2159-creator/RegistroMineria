from app import app
from extensions import mysql

def fix_sp_crearregistro_select():
    """
    El problema: pymysql CALL devuelve multiples result sets.
    El INSERT no produce rows, pero puede causar que sp_exec lea
    el result set equivocado. Solucion: usar LAST_INSERT_ID() directo
    en la misma query de SELECT.
    """
    with app.app_context():
        cur = mysql.connection.cursor()
        
        cur.execute("DROP PROCEDURE IF EXISTS sp_crearregistro")
        
        sp_sql = """
        CREATE PROCEDURE sp_crearregistro(
            IN p_codigo VARCHAR(20),
            IN p_fechainicio DATETIME,
            IN p_fechaejecucion DATETIME,
            IN p_descripcion VARCHAR(500),
            IN p_accion VARCHAR(300),
            IN p_idareareportante INT,
            IN p_personalreportante INT,
            IN p_idarearesponsable INT,
            IN p_ubicacion VARCHAR(200),
            IN p_idriesgo INT,
            IN p_iddescripciontipo INT,
            IN p_riesgo_critico_id INT,
            IN p_idestado INT,
            IN p_idusuariorolcreador INT,
            IN p_personalresponsable_id INT,
            IN p_cctaresponsable INT,
            IN p_dniresponsable VARCHAR(20),
            IN p_idorigen INT
        )
        BEGIN
            DECLARE v_id INT;
            
            INSERT INTO tbl_registro (
                codigo, fechainicio, fechaejecucion, descripcion, accion,
                idareareportante, personalreportante, idarearesponsable, ubicacion, idriesgo,
                iddescripciontipo, riesgo_critico_id, idestado, idusuariorolcreador,
                personalresponsable_id, cctaresponsable, DniResponsable,
                idorigen, fechacreacion, fechaactualizacion
            ) VALUES (
                p_codigo, p_fechainicio, p_fechaejecucion, p_descripcion, p_accion,
                p_idareareportante, NULLIF(p_personalreportante, 0), p_idarearesponsable,
                p_ubicacion, p_idriesgo, p_iddescripciontipo, NULLIF(p_riesgo_critico_id, 0),
                p_idestado, p_idusuariorolcreador, NULLIF(p_personalresponsable_id, 0),
                NULLIF(p_cctaresponsable, 0), NULLIF(p_dniresponsable, ''),
                p_idorigen, NOW(), NOW()
            );
            
            SET v_id = LAST_INSERT_ID();
            SELECT v_id AS idregistro;
        END
        """
        
        cur.execute(sp_sql)
        mysql.connection.commit()
        print("OK: sp_crearregistro actualizado con DECLARE + SET + SELECT para resultado limpio")
        cur.close()

if __name__ == '__main__':
    fix_sp_crearregistro_select()
