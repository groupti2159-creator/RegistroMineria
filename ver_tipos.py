#!/usr/bin/env python
# -*- coding: utf-8 -*-
from extensions import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tbl_descripciontipo ORDER BY descripciontipo")
    print("=== TIPOS ACTUALES ===")
    for row in cur.fetchall():
        print(f"{row['iddescripciontipo']:3d}: {row['descripciontipo']}")
    cur.close()
