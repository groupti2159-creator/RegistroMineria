#!/usr/bin/env python
# -*- coding: utf-8 -*-
from extensions import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("DESCRIBE tbl_registro")
    print("=== Campo ubicacion en tbl_registro ===")
    for col in cur.fetchall():
        if 'ubicacion' in col['Field'].lower():
            print(f"{col['Field']:30s} {col['Type']:20s} {col['Null']:5s} {col['Key']:5s}")
    cur.close()
