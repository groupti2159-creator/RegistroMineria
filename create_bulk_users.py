#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para crear múltiples usuarios con contraseña por defecto 123456@
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from extensions import mysql

# Datos de usuarios a crear
usuarios_data = [
    ("10312678", "PERCY CHÁVEZ ROJAS", "SUPERVISOR"),
    ("43415362", "PERCY VILLANES CCALA", "SUPERVISOR"),
    ("41604043", "NAHUN CHUQUITARQUI AROQUIPA", "SUPERVISOR"),
    ("44532952", "ADRIAN CARHUAMACA CORDOVA", "SUPERVISOR"),
    ("75910357", "ALEXIS AGUILAR CHOQUECAHUANA", "SUPERVISOR"),
    ("70603124", "FRANK PILLACA AGUIRRE", "SUPERVISOR"),
    ("76412170", "BALAN SERGIO CHURA QUISPE", "SUPERVISOR"),
    ("41788724", "ELMER CUTIPA CUTIPA", "SUPERVISOR"),
    ("40476645", "JOSÉ FERNANDEZ ALCANTARA", "SUPERVISOR"),
    ("03895501", "PERCY SALDARRIAGA ESPINOZA", "SUPERVISOR"),
    ("40399631", "FREDDY QUISPE JIMENEZ", "SUPERVISOR"),
    ("74302558", "YANETH DURAN GASPAR", "SUPERVISOR"),
    ("42665068", "EDINSON D. CRUZ GARCIA", "SUPERVISOR"),
    ("46194999", "FRANCO F. SILVESTRE GALLARDO", "SUPERVISOR"),
    ("47510033", "RAUL HUACHACA GOMEZ", "SUPERVISOR"),
    ("45639929", "INTI L. VERA ZELA", "SUPERVISOR"),
    ("44940761", "FRANZ J FERNANDEZ ROJAS", "SUPERVISOR"),
    ("74965355", "EDWAR COPA PUMA", "SUPERVISOR"),
    ("60690496", "EDWIN HUARACALLO COA", "SUPERVISOR"),
    ("44768263", "DONATO COILA APAZA", "SUPERVISOR"),
    ("60648220", "ROGER TICONA MAMANI", "SUPERVISOR"),
    ("41422401", "RAMIRO RODRIGO SUPO OLARTE", "SUPERVISOR"),
    ("74402649", "ROLANDO CANAZA CUNO", "SUPERVISOR"),
    ("42536474", "VIDAL PACCAYA CONDORI", "SUPERVISOR"),
    ("70171041", "HENRY QUISPE FLORES", "SUPERVISOR"),
    ("70544428", "WILDER DIAZ HUALINGA", "SUPERVISOR"),
    ("02437383", "JHONATTAN TANTALEAN CARRANZA", "SUPERVISOR"),
    ("70216209", "EDWAR LLANQUE MAMANI", "SUPERVISOR"),
    ("73102508", "JHOSEP A. CARREÑO ROSALES", "SUPERVISOR"),
    ("75852685", "FRANCK A. LEIVA GARRIDO", "SUPERVISOR"),
    ("46659286", "RODRIGO ARAGON YAURIS", "SUPERVISOR"),
    ("72536099", "JOVEL PAMINO GARCIA", "SUPERVISOR"),
    ("47275196", "CARLOS ANDRES POZO BULNES", "SUPERVISOR"),
    ("41024964", "VIDAL A. PEÑA ANDRADE", "SUPERVISOR"),
    ("72299049", "WILFREDO S. MALLMA HUAMANI", "SUPERVISOR"),
    ("43548273", "JOSE CESPEDES RIVADENEIRA", "SUPERVISOR"),
    ("04745176", "ERNESTO M. TITO CUTIPA", "SUPERVISOR"),
    ("70671374", "GIULIANNA MOTTA SANTILLAN", "AUDITOR"),
    ("70102590", "URIEL CHAMBI GUTIERREZ", "AUDITOR"),
    ("73219409", "DERBITH CARLA CARRAZGO CHIRINOS", "AUDITOR"),
    ("44226823", "MILUSKA LUY FABABA", "AUDITOR"),
    ("73376856", "ALEXANNDER DEL AGUILA SANTIAGO", "SUPERVISOR"),
    ("73450906", "RAUL NILTON GUTIERREZ QUISPE", "SUPERVISOR"),
    ("71440949", "MARYELIN RIVERA LACUTA", "SUPERVISOR"),
    ("41444973", "JORGE YSLA MANTILLA", "SUPERVISOR"),
    ("41654633", "GEANCARLO SHAPIAMA SINTI", "SUPERVISOR"),
    ("42782047", "JOSE ROGELIO BARRANTES CCAPA", "SUPERVISOR"),
    ("43436576", "HUGO CUSIHUAMAN LLANQUE", "SUPERVISOR"),
    ("05863506", "GILBERT MOZONBITE TORRES", "SUPERVISOR"),
]

def create_users():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            # Obtener el ID del rol Supervisor y Auditor
            cur.execute("SELECT idroles FROM tbl_roles WHERE nombrerol = 'Supervisor'")
            supervisor_rol = cur.fetchone()
            
            cur.execute("SELECT idroles FROM tbl_roles WHERE nombrerol = 'Auditor'")
            auditor_rol = cur.fetchone()
            
            if not supervisor_rol or not auditor_rol:
                print("✗ No se encontraron los roles Supervisor o Auditor")
                return False
            
            supervisor_id = supervisor_rol['idroles']
            auditor_id = auditor_rol['idroles']
            
            print(f"Supervisor ID: {supervisor_id}")
            print(f"Auditor ID: {auditor_id}")
            print("-" * 80)
            
            created = 0
            skipped = 0
            errors = 0
            
            for dni, nombre, rol_nombre in usuarios_data:
                try:
                    # Verificar si el usuario ya existe
                    cur.execute("SELECT idusuario FROM tbl_usuario WHERE idusuario = %s", (dni,))
                    if cur.fetchone():
                        print(f"⊘ {dni} - {nombre} (YA EXISTE)")
                        skipped += 1
                        continue
                    
                    # Determinar el ID del rol
                    rol_id = supervisor_id if rol_nombre == 'SUPERVISOR' else auditor_id
                    
                    # Crear el usuario con contraseña por defecto 123456@
                    password = '123456@'
                    cur.execute("""
                        INSERT INTO tbl_usuario (idusuario, nombrecompleto, contrasena, activo, fechacreacion)
                        VALUES (%s, %s, MD5(%s), 1, NOW())
                    """, (dni, nombre, password))
                    
                    # Obtener el ID del usuario creado
                    user_id = dni
                    
                    # Asignar al proyecto 1 (Argos) con el rol correspondiente
                    cur.execute("""
                        INSERT INTO tbl_usuariorol (idusuario, idproyecto, idroles)
                        VALUES (%s, 1, %s)
                    """, (user_id, rol_id))
                    
                    mysql.connection.commit()
                    print(f"✓ {dni} - {nombre} ({rol_nombre})")
                    created += 1
                    
                except Exception as e:
                    mysql.connection.rollback()
                    print(f"✗ {dni} - {nombre} - Error: {str(e)}")
                    errors += 1
            
            cur.close()
            
            print("-" * 80)
            print(f"\n📊 Resumen:")
            print(f"  ✓ Creados: {created}")
            print(f"  ⊘ Saltados (ya existen): {skipped}")
            print(f"  ✗ Errores: {errors}")
            print(f"  Total procesados: {len(usuarios_data)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error general: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = create_users()
    sys.exit(0 if success else 1)
