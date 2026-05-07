#!/usr/bin/env python
# -*- coding: utf-8 -*-
from extensions import mysql
from app import app

with app.app_context():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = 'desvios_ambientales'
          AND TABLE_NAME = 'tbl_registro'
          AND REFERENCED_TABLE_NAME IS NOT NULL
    """)
    print("=== FOREIGN KEYS en tbl_registro ===")
    for row in cur.fetchall():
        print(f"{row['CONSTRAINT_NAME']:30s} {row['COLUMN_NAME']:20s} -> {row['REFERENCED_TABLE_NAME']}.{row['REFERENCED_COLUMN_NAME']}")
    cur.close()
