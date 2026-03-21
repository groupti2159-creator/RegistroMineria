import MySQLdb

conn = MySQLdb.connect(host='centerbeam.proxy.rlwy.net', port=12842, user='root',
                       passwd='xjIkFDMLeGlztTsaAlDIjEQpVKiObtPj', db='desvios_ambientales')
conn.autocommit = False
cur = conn.cursor()

try:
    # Verificar estado actual de tbl_usuariorol
    cur.execute("DESCRIBE tbl_usuariorol")
    cols = {r[0]: r for r in cur.fetchall()}
    ya_migrado_ur = 'dni' in cols and 'idusuario' not in cols
    print(f"tbl_usuariorol ya migrada: {ya_migrado_ur}")

    cur.execute("DESCRIBE tbl_usuario")
    cols_u = {r[0]: r for r in cur.fetchall()}
    ya_migrado_u = 'idusuario' not in cols_u
    print(f"tbl_usuario ya migrada: {ya_migrado_u}")

    print("\n1. Dropeando FK existente...")
    try:
        cur.execute("ALTER TABLE tbl_usuariorol DROP FOREIGN KEY tbl_usuariorol_ibfk_1")
        print("   FK dropeada")
    except Exception as e:
        print(f"   FK ya no existe o error: {e}")

    if not ya_migrado_ur:
        print("2. Migrando idusuario -> dni en tbl_usuariorol...")
        cur.execute("""
            UPDATE tbl_usuariorol ur
            JOIN tbl_usuario u ON u.idusuario = ur.idusuario
            SET ur.idusuario = u.dni
        """)
        print(f"   Filas actualizadas: {cur.rowcount}")
    else:
        print("2. tbl_usuariorol ya tiene columna dni, saltando UPDATE")

    if not ya_migrado_u:
        print("3. Dropeando PK y columna idusuario de tbl_usuario...")
        cur.execute("ALTER TABLE tbl_usuario DROP PRIMARY KEY")
        cur.execute("ALTER TABLE tbl_usuario DROP COLUMN idusuario")
        cur.execute("ALTER TABLE tbl_usuario ADD PRIMARY KEY (dni)")
        print("   PK cambiada a dni")
    else:
        print("3. tbl_usuario ya no tiene idusuario, saltando")

    if not ya_migrado_ur:
        print("4. Renombrando columna idusuario -> dni en tbl_usuariorol...")
        cur.execute("ALTER TABLE tbl_usuariorol CHANGE idusuario dni VARCHAR(20) NOT NULL")
        print("   Columna renombrada")
    else:
        print("4. Columna ya es dni, saltando")

    print("5. Recreando FK con ON UPDATE CASCADE...")
    try:
        cur.execute("""
            ALTER TABLE tbl_usuariorol
            ADD CONSTRAINT tbl_usuariorol_ibfk_1
            FOREIGN KEY (dni) REFERENCES tbl_usuario(dni)
            ON DELETE CASCADE ON UPDATE CASCADE
        """)
        print("   FK recreada")
    except Exception as e:
        print(f"   FK ya existe o error: {e}")

    conn.commit()
    print("\n✅ Migración completada.")

    cur.execute("DESCRIBE tbl_usuario")
    print("\ntbl_usuario:")
    for r in cur.fetchall(): print(" ", r)

    cur.execute("DESCRIBE tbl_usuariorol")
    print("\ntbl_usuariorol:")
    for r in cur.fetchall(): print(" ", r)

    cur.execute("SELECT * FROM tbl_usuariorol")
    print("\nDatos tbl_usuariorol:")
    for r in cur.fetchall(): print(" ", r)

except Exception as e:
    conn.rollback()
    print(f"\n❌ ERROR: {e}")
    raise
finally:
    cur.close()
    conn.close()
