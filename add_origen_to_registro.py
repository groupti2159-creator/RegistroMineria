#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para agregar la columna idorigen a tbl_registro y actualizar los SPs
"""

from app import app
from extensions import mysql

def add_origen_column():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Verificar si la columna ya existe
            cur.execute("SHOW COLUMNS FROM tbl_registro LIKE 'idorigen'")
            if cur.fetchone():
                print("✓ La columna 'idorigen' ya existe en tbl_registro")
                cur.close()
                return
            
            # Agregar la columna
            print("Agregando columna 'idorigen' a tbl_registro...")
            cur.execute("""
                ALTER TABLE tbl_registro 
                ADD COLUMN idorigen INT DEFAULT 1 
                AFTER ubicacion
            """)
            mysql.connection.commit()
            print("✓ Columna 'idorigen' agregada exitosamente")
            
            # Agregar constraint de clave foránea
            print("Agregando constraint de clave foránea...")
            cur.execute("""
                ALTER TABLE tbl_registro 
                ADD CONSTRAINT fk_registro_origen 
                FOREIGN KEY (idorigen) REFERENCES tbl_origen(idorigen)
            """)
            mysql.connection.commit()
            print("✓ Constraint de clave foránea agregado")
            
            cur.close()
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

def update_sp_crearregistro():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("\nActualizando sp_crearregistro...")
            
            # Eliminar el SP si existe
            cur.execute("DROP PROCEDURE IF EXISTS sp_crearregistro")
            mysql.connection.commit()
            
            # Crear el nuevo SP
            sp_sql = """
            CREATE PROCEDURE sp_crearregistro(
                IN p_codigo VARCHAR(20),
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
                IN p_idusuariorolcreador INT,
                IN p_personalresponsable VARCHAR(100),
                IN p_cctaresponsable INT,
                IN p_dniresponsable VARCHAR(20),
                IN p_idorigen INT
            )
            BEGIN
                INSERT INTO tbl_registro (
                    codigo, fechainicio, fechaejecucion, descripcion, accion,
                    idareareportante, idarearesponsable, ubicacion, idriesgo,
                    iddescripciontipo, idestado, idusuariorolcreador,
                    personalresponsable, cctaresponsable, DniResponsable,
                    idorigen, fechacreacion, fechaactualizacion
                ) VALUES (
                    p_codigo, p_fechainicio, p_fechaejecucion, p_descripcion, p_accion,
                    p_idareareportante, p_idarearesponsable, p_ubicacion, p_idriesgo,
                    p_iddescripciontipo, p_idestado, p_idusuariorolcreador,
                    p_personalresponsable, p_cctaresponsable, p_dniresponsable,
                    p_idorigen, NOW(), NOW()
                );
                
                SELECT LAST_INSERT_ID() as idregistro;
            END
            """
            
            cur.execute(sp_sql)
            mysql.connection.commit()
            print("✓ sp_crearregistro actualizado")
            
            cur.close()
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

def update_sp_actualizarregistro():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("\nActualizando sp_actualizarregistro...")
            
            # Eliminar el SP si existe
            cur.execute("DROP PROCEDURE IF EXISTS sp_actualizarregistro")
            mysql.connection.commit()
            
            # Crear el nuevo SP
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
                    personalresponsable = p_personalresponsable,
                    cctaresponsable = p_cctaresponsable,
                    DniResponsable = p_dniresponsable,
                    idorigen = p_idorigen,
                    fechaactualizacion = NOW()
                WHERE idregistro = p_idregistro;
                
                SELECT ROW_COUNT() as rows_affected;
            END
            """
            
            cur.execute(sp_sql)
            mysql.connection.commit()
            print("✓ sp_actualizarregistro actualizado")
            
            cur.close()
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=" * 50)
    print("AGREGANDO SOPORTE PARA ORIGEN EN REGISTROS")
    print("=" * 50)
    
    add_origen_column()
    update_sp_crearregistro()
    update_sp_actualizarregistro()
    
    print("\n" + "=" * 50)
    print("✓ PROCESO COMPLETADO")
    print("=" * 50)
