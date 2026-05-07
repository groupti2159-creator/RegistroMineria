#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para crear tabla tbl_personas y agregar datos"""

from extensions import mysql
from app import app

def crear_tabla_personas():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Crear tabla
            print("Creando tabla tbl_personas...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tbl_personas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    NombresCompletos VARCHAR(200) NOT NULL,
                    idareareportante INT NOT NULL,
                    activo TINYINT(1) DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (idareareportante) REFERENCES tbl_areareportante(idareareportante) ON DELETE CASCADE,
                    INDEX idx_area (idareareportante),
                    INDEX idx_activo (activo)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            print("  ✓ Tabla creada")
            
            # Datos a insertar
            personas = [
                ('PERCY CHÁVEZ ROJAS', 7),
                ('PERCY VILLANES CCALA', 7),
                ('NAHUN CHUQUITARQUI AROQUIPA', 8),
                ('ADRIAN CARHUAMACA CORDOVA', 9),
                ('ALEXIS AGUILAR CHOQUECAHUANA', 9),
                ('FRANK PILLACA AGUIRRE', 9),
                ('BALAN SERGIO CHURA QUISPE', 9),
                ('ELMER CUTIPA CUTIPA', 9),
                ('JOSÉ FERNANDEZ ALCANTARA', 9),
                ('PERCY SALDARRIAGA ESPINOZA', 9),
                ('FREDDY QUISPE JIMENEZ', 9),
                ('YANETH DURAN GASPAR', 10),
                ('EDINSON D. CRUZ GARCIA', 11),
                ('FRANCO F. SILVESTRE GALLARDO', 12),
                ('RAUL HUACHACA GOMEZ', 12),
                ('INTI L. VERA ZELA', 12),
                ('FRANZ J FERNANDEZ ROJAS', 12),
                ('EDWAR COPA PUMA', 12),
                ('EDWIN HUARACALLO COA', 12),
                ('DONATO COILA APAZA', 12),
                ('ROGER TICONA MAMANI', 12),
                ('RAMIRO RODRIGO SUPO OLARTE', 12),
                ('ROLANDO CANAZA CUNO', 12),
                ('VIDAL PACCAYA CONDORI', 12),
                ('HENRY QUISPE FLORES', 12),
                ('WILDER DIAZ HUALINGA', 13),
                ('JHONATTAN TANTALEAN CARRANZA', 13),
                ('EDWAR LLANQUE MAMANI', 13),
                ('JHOSEP A. CARREÑO ROSALES', 14),
                ('FRANCK A. LEIVA GARRIDO', 14),
                ('RODRIGO ARAGON YAURIS', 14),
                ('JOVEL PAMINO GARCIA', 14),
                ('CARLOS ANDRES POZO BULNES', 14),
                ('VIDAL A. PEÑA ANDRADE', 15),
                ('WILFREDO S. MALLMA HUAMANI', 15),
                ('JOSE CESPEDES RIVADENEIRA', 15),
                ('ERNESTO M. TITO CUTIPA', 16),
                ('YHONY A. SANCA HALLASI', 17),
                ('GIULIANNA MOTTA SANTILLAN', 18),
                ('URIEL CHAMBI GUTIERREZ', 18),
                ('DERBITH CARLA CARRAZGO CHIRINOS', 18),
                ('MILUSKA LUY FABABA', 18),
                ('ALEXANNDER DEL AGUILA SANTIAGO', 18),
                ('RAUL NILTON GUTIERREZ QUISPE', 18),
                ('JOSE FERNANDEZ', 18),
                ('MARYELIN RIVERA LACUTA', 18),
                ('JORGE YSLA MANTILLA', 18),
                ('GEANCARLO SHAPIAMA SINTI', 19),
                ('JOSE ROGELIO BARRANTES CCAPA', 19),
                ('HUGO CUSIHUAMAN LLANQUE', 19),
                ('GILBERT MOZONBITE TORRES', 19)
            ]
            
            print(f"\nInsertando {len(personas)} personas...")
            for nombre, area_id in personas:
                cur.execute(
                    "INSERT INTO tbl_personas (NombresCompletos, idareareportante) VALUES (%s, %s)",
                    (nombre, area_id)
                )
                print(f"  ✓ {nombre}")
            
            mysql.connection.commit()
            
            # Mostrar resumen
            print("\n=== RESUMEN POR ÁREA ===")
            cur.execute("""
                SELECT 
                    a.areareportante,
                    COUNT(p.id) as total_personas
                FROM tbl_areareportante a
                LEFT JOIN tbl_personas p ON a.idareareportante = p.idareareportante
                WHERE p.id IS NOT NULL
                GROUP BY a.idareareportante, a.areareportante
                ORDER BY a.areareportante
            """)
            
            for row in cur.fetchall():
                print(f"{row['areareportante']:40s} : {row['total_personas']:2d} personas")
            
            # Total
            cur.execute("SELECT COUNT(*) as total FROM tbl_personas")
            total = cur.fetchone()['total']
            print(f"\n{'TOTAL':40s} : {total:2d} personas")
            
            cur.close()
            print("\n✅ Tabla y datos creados exitosamente")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    crear_tabla_personas()
