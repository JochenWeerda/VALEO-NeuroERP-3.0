#!/usr/bin/env python3
"""Simple DB connection test from Windows to Docker PostgreSQL"""

import psycopg2

DATABASE_URL = "postgresql://valeo_dev:valeo_dev_2024!@127.0.0.1:5432/valeo_neuro_erp"

print("Testing PostgreSQL connection from Windows to Docker...")
print(f"URL: {DATABASE_URL}")

try:
    conn = psycopg2.connect(
        database="valeo_neuro_erp",
        user="valeo_dev",
        password="valeo_dev_2024!",
        host="127.0.0.1",
        port=5432
    )
    print("✅ Connection successful!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT current_database(), current_user, version();")
    row = cursor.fetchone()
    print(f"   Database: {row[0]}")
    print(f"   User: {row[1]}")
    print(f"   Version: {row[2][:50]}...")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()

