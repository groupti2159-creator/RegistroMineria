from app import app
from extensions import mysql

def fix_sp_actualizar():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        cur.execute("DROP PROCEDURE IF EXISTS sp_actualizarregistro")
        
        sp_sql = """
        CREATE PROCEDURE sp_actualizarregistro(
            IN p_idregistro INT,
            IN p_fechainicio DATETIME,
            IN p_fechaejecucion DATETIME,
            IN p_descripcion VARCHAR(500),
            IN p_accion VARCHAR(300),
            IN p_idareareportante INT,
            IN p_idarearesponsable INT,
            IN p_ubicacion VARCHAR(200),
            IN p_idriesgo INT,
            IN p_iddescripciontipo INT,
            IN p_idestado INT,
            IN p_personalresponsable VARCHAR(100),
            IN p_cctaresponsable INT,
            IN p_dniresponsable VARCHAR(20),
            IN p_idorigen INT
        )
        BEGIN
            UPDATE tbl_registro SET
                fechainicio = p_fechainicio,
                fechaejecucion = p_fechaejecucion,
                descripcion = p_descripcion,
                accion = p_accion,
                idareareportante = p_idareareportante,
                idarearesponsable = p_idarearesponsable,
                ubicacion = p_ubicacion,
                idriesgo = p_idriesgo,
                iddescripciontipo = p_iddescripciontipo,
                idestado = p_idestado,
                personalresponsable = NULLIF(p_personalresponsable, ''),
                cctaresponsable = NULLIF(p_cctaresponsable, 0),
                DniResponsable = NULLIF(p_dniresponsable, ''),
                idorigen = p_idorigen,
                fechaactualizacion = NOW()
            WHERE idregistro = p_idregistro;
            
            SELECT ROW_COUNT() as rows_affected;
        END
        """
        
        cur.execute(sp_sql)
        mysql.connection.commit()
        print("OK: sp_actualizarregistro actualizado con NULLIF para cctaresponsable")
        cur.close()

if __name__ == '__main__':
    fix_sp_actualizar()
