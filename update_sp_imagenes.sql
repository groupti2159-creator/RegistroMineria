USE desvios_ambientales;

DELIMITER $$

DROP PROCEDURE IF EXISTS SP_ImagenesRegistro$$
CREATE PROCEDURE SP_ImagenesRegistro(IN p_id CHAR(18))
BEGIN
    SELECT i.IdImagen, i.RutaImagen, i.NombreArchivo, i.TamanoKB,
           i.MotivoRechazo, i.FechaSubida, i.FechaRevision,
           ti.TipoImagen, ti.idTipoImagen,
           ei.EstadoImagen, ei.idEstadoImagen,
           u.NombreCompleto AS Subidor
    FROM Tbl_ImagenRegistro i
    JOIN Tbl_TipoImagen ti ON ti.idTipoImagen = i.idTipoImagen
    JOIN Tbl_EstadoImagen ei ON ei.idEstadoImagen = i.idEstadoImagen
    JOIN Tbl_UsuarioRol ur ON ur.IdUsuarioRol = i.IdUsuarioRol
    JOIN Tbl_Usuario u ON u.idUsuario = ur.idUsuario
    WHERE i.IdRegistro = p_id
      AND i.idEstadoImagen != 'EIM003'
    ORDER BY i.FechaSubida;
END$$

DELIMITER ;
