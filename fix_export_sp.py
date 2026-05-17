from app import app
from extensions import mysql

with app.app_context():
    cur = mysql.connection.cursor()
    
    print('Actualizando sp_exportarregistros...')
    
    # Eliminar el SP si existe
    cur.execute('DROP PROCEDURE IF EXISTS sp_exportarregistros')
    mysql.connection.commit()
    
    # Crear el nuevo SP sin el JOIN a tbl_ubicacion
    sp_sql = '''
    CREATE PROCEDURE sp_exportarregistros()
    BEGIN
        SELECT r.IdRegistro,
               r.Codigo, DATE(r.FechaInicio) AS Fecha,
               DATE(r.FechaEjecucion) AS FechaEjecucion,
               ar.AreaReportante, r.Ubicacion,
               r.Descripcion, dt.DescripcionTipo,
               ri.Riesgo, e.Estado, r.Accion,
               ars.AreaResponsable, r.PersonalResponsable,
               r.FechaCreacion
        FROM tbl_registro r
        JOIN tbl_estado e ON e.idEstado=r.idEstado
        JOIN tbl_areareportante ar ON ar.idAreaReportante=r.idAreaReportante
        JOIN tbl_arearesponsable ars ON ars.idAreaResponsable=r.idAreaResponsable
        JOIN tbl_riesgo ri ON ri.IdRiesgo=r.IdRiesgo
        JOIN tbl_descripciontipo dt ON dt.IdDescripcionTipo=r.IdDescripcionTipo
        WHERE r.Archivado=0
        ORDER BY r.FechaCreacion DESC;
    END
    '''
    
    cur.execute(sp_sql)
    mysql.connection.commit()
    print('SP actualizado exitosamente')
    
    cur.close()
