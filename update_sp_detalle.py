#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para actualizar sp_detalleregistro para incluir idorigen
"""

from app import app
from extensions import mysql

def update_sp_detalleregistro():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("Actualizando sp_detalleregistro...")
            
            # Eliminar el SP si existe
            cur.execute("DROP PROCEDURE IF EXISTS sp_detalleregistro")
            mysql.connection.commit()
            
            # Crear el nuevo SP
            sp_sql = """
            CREATE PROCEDURE sp_detalleregistro(
                IN p_idregistro INT
            )
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
                    r.idubicacion,
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
            print("✓ sp_detalleregistro actualizado")
            
            cur.close()
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=" * 50)
    print("ACTUALIZANDO sp_detalleregistro")
    print("=" * 50)
    
    update_sp_detalleregistro()
    
    print("\n" + "=" * 50)
    print("✓ PROCESO COMPLETADO")
    print("=" * 50)
