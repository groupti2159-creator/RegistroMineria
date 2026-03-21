import MySQLdb

conn = MySQLdb.connect(
    host='centerbeam.proxy.rlwy.net', port=12842,
    user='root', passwd='xjIkFDMLeGlztTsaAlDIjEQpVKiObtPj',
    db='desvios_ambientales', charset='utf8mb4'
)
cur = conn.cursor()
cur.execute("SET FOREIGN_KEY_CHECKS=0")

cur.execute("SHOW TABLES")
tablas = [r[0] for r in cur.fetchall()]
print("Tablas existentes:", tablas)

for t in tablas:
    cur.execute(f"DESCRIBE {t}")
    cols = cur.fetchall()
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    cnt = cur.fetchone()[0]
    pk = next((c for c in cols if 'PRI' in str(c)), None)
    pk_type = pk[1] if pk else '?'
    print(f"  {t}: {cnt} filas, PK type={pk_type}")

cur.close()
conn.close()
