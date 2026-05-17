from app import app
from extensions import mysql

def fix_sp_listar():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        cur.execute("DROP PROCEDURE IF EXISTS sp_listarregistros")
        
        sp_sql = """
        CREATE PROCEDURE sp_listarregistros(IN p_estado VARCHAR(50))
        BEGIN
            SELECT 
                r.IdRegistro,
                r.Codigo,
                r.FechaInicio,
                r.FechaEjecucion,
                r.Descripcion,
                r.Accion,
                ar.AreaReportante,
                ar.idAreaReportante,
                ars.AreaResponsable,
                ars.idAreaResponsable,
                r.ubicacion AS Ubicacion,
                ri.Riesgo,
                ri.IdRiesgo,
                dt.DescripcionTipo,
                dt.IdDescripcionTipo,
                e.Estado,
                e.idEstado,
                r.PersonalResponsable,
                r.DniResponsable,
                r.FechaCreacion,
                r.FechaActualizacion,
                ccta.AreaReportante AS NombreCctaResponsable,
                (SELECT COUNT(*) FROM tbl_imagenregistro i 
                 WHERE i.IdRegistro = r.IdRegistro 
                   AND i.idTipoImagen = 1 
                   AND i.idEstadoImagen != 3) AS cnt_evidencias,
                (SELECT COUNT(*) FROM tbl_imagenregistro i 
                 WHERE i.IdRegistro = r.IdRegistro 
                   AND i.idTipoImagen = 2 
                   AND i.idEstadoImagen != 3) AS cnt_levantamientos
            FROM tbl_registro r
            JOIN tbl_estado e ON e.idEstado = r.idEstado
            JOIN tbl_areareportante ar ON ar.idAreaReportante = r.idAreaReportante
            JOIN tbl_arearesponsable ars ON ars.idAreaResponsable = r.idAreaResponsable
            JOIN tbl_riesgo ri ON ri.IdRiesgo = r.IdRiesgo
            JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo = r.IdDescripcionTipo
            LEFT JOIN tbl_areareportante ccta ON ccta.idAreaReportante = r.cctaresponsable
            WHERE (p_estado IS NULL OR e.Estado = p_estado)
              AND (r.Archivado IS NULL OR r.Archivado = 0)
            ORDER BY r.FechaCreacion DESC;
        END
        """
        
        cur.execute(sp_sql)
        mysql.connection.commit()
        print("OK: sp_listarregistros actualizado con cnt_evidencias y cnt_levantamientos")
        cur.close()

if __name__ == '__main__':
    fix_sp_listar()
