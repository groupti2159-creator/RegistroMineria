"""
Script para implementar menú 100% dinámico desde la base de datos
Permite cambiar nombres, iconos y orden sin tocar código
"""
from app import app
from extensions import mysql

def implementar_menu_dinamico():
    with app.app_context():
        try:
            cur = mysql.connection.cursor()
            
            print("=" * 80)
            print("🚀 IMPLEMENTANDO MENÚ 100% DINÁMICO")
            print("=" * 80)
            
            # PASO 1: Establecer relaciones padre-hijo
            print("\n📁 PASO 1: Estableciendo relaciones padre-hijo...")
            
            relaciones = [
                # Desvíos SSOMA (padre: 25)
                (25, [1, 2, 3], "Desvíos SSOMA"),
                # Gestión de Residuos (padre: 16)
                (16, [17, 18, 19, 20], "Gestión de Residuos"),
                # Compromisos (padre: 30)
                (30, [26, 29], "Compromisos"),
                # Data Meteorológica (padre: 32)
                (32, [27, 31], "Data Meteorológica"),
                # Configuración (padre: 4)
                (4, [28, 45], "Configuración"),
                # Gestión de Aguas (padre: 33)
                (33, [34, 35, 36], "Gestión de Aguas"),
            ]
            
            for padre_id, hijos_ids, nombre_grupo in relaciones:
                for hijo_id in hijos_ids:
                    cur.execute("""
                        UPDATE tbl_modulo 
                        SET idmodulopadre = %s 
                        WHERE idmodulo = %s
                    """, (padre_id, hijo_id))
                print(f"  ✓ {nombre_grupo}: {len(hijos_ids)} hijos asignados")
            
            # PASO 2: Actualizar nombres de módulos padre
            print("\n✏️  PASO 2: Actualizando nombres de grupos...")
            
            nombres = [
                (25, "Desvíos SSOMA"),
                (16, "Gestión de Residuos"),
                (30, "Compromisos"),
                (32, "Data Meteorológica"),
                (4, "Configuración"),
                (33, "Gestión de Aguas"),
            ]
            
            for modulo_id, nombre in nombres:
                cur.execute("""
                    UPDATE tbl_modulo 
                    SET nombre = %s 
                    WHERE idmodulo = %s
                """, (nombre, modulo_id))
                print(f"  ✓ [{modulo_id}] → {nombre}")
            
            # PASO 3: Eliminar duplicados
            print("\n🗑️  PASO 3: Eliminando módulos duplicados...")
            
            cur.execute("SELECT COUNT(*) as count FROM tbl_modulo WHERE idmodulo = 62")
            existe = cur.fetchone()
            
            if existe and existe['count'] > 0:
                cur.execute("DELETE FROM tbl_proyecto_rol_modulo WHERE idmodulo = 62")
                cur.execute("DELETE FROM tbl_modulo WHERE idmodulo = 62")
                print("  ✓ Módulo duplicado (id=62) eliminado")
            else:
                print("  ℹ️  No hay módulos duplicados")
            
            # Confirmar cambios
            mysql.connection.commit()
            
            print("\n" + "=" * 80)
            print("✅ MENÚ DINÁMICO IMPLEMENTADO EXITOSAMENTE")
            print("=" * 80)
            
            # PASO 4: Verificar estructura
            print("\n📊 VERIFICANDO ESTRUCTURA FINAL...\n")
            
            cur.execute("""
                SELECT idmodulo, codigo, nombre, icono, orden
                FROM tbl_modulo
                WHERE idmodulopadre IS NULL AND activo = 1
                ORDER BY orden
            """)
            padres = cur.fetchall()
            
            print(f"📁 MÓDULOS PADRE: {len(padres)}\n")
            
            for padre in padres:
                print(f"  [{padre['idmodulo']}] {padre['nombre']}")
                print(f"      Icono: {padre['icono']} | Orden: {padre['orden']}")
                
                cur.execute("""
                    SELECT idmodulo, codigo, nombre, url, orden
                    FROM tbl_modulo
                    WHERE idmodulopadre = %s AND activo = 1
                    ORDER BY orden
                """, (padre['idmodulo'],))
                hijos = cur.fetchall()
                
                if hijos:
                    print(f"      Hijos ({len(hijos)}):")
                    for hijo in hijos:
                        print(f"         └─ [{hijo['idmodulo']}] {hijo['nombre']} → {hijo['url']}")
                else:
                    print(f"      ⚠️  Sin hijos asignados")
                print()
            
            # Módulos sin padre (huérfanos)
            cur.execute("""
                SELECT idmodulo, codigo, nombre, url
                FROM tbl_modulo
                WHERE idmodulopadre IS NOT NULL 
                  AND idmodulopadre NOT IN (SELECT idmodulo FROM tbl_modulo)
                  AND activo = 1
            """)
            huerfanos = cur.fetchall()
            
            if huerfanos:
                print("⚠️  MÓDULOS HUÉRFANOS (padre no existe):")
                for h in huerfanos:
                    print(f"  [{h['idmodulo']}] {h['nombre']}")
            
            cur.close()
            
            print("\n" + "=" * 80)
            print("💡 AHORA PUEDES:")
            print("   1. Cambiar nombres: UPDATE tbl_modulo SET nombre='Nuevo Nombre' WHERE idmodulo=25")
            print("   2. Cambiar iconos: UPDATE tbl_modulo SET icono='star' WHERE idmodulo=25")
            print("   3. Cambiar orden: UPDATE tbl_modulo SET orden=5 WHERE idmodulo=25")
            print("   4. ¡Los cambios se reflejan automáticamente en el menú!")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            mysql.connection.rollback()

if __name__ == "__main__":
    print("\n⚠️  ADVERTENCIA: Este script modificará la estructura de tu base de datos.")
    print("   Se recomienda hacer un backup antes de continuar.\n")
    
    respuesta = input("¿Deseas continuar? (s/n): ")
    
    if respuesta.lower() == 's':
        implementar_menu_dinamico()
    else:
        print("\n❌ Operación cancelada")
