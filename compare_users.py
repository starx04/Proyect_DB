import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def get_columns(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
        """)
        return cursor.fetchall()

print("--- Table: usuarios ---")
for col in get_columns('usuarios'):
    print(f"{col[0]}: {col[1]}")

print("\n--- Table: accounts_usuario ---")
for col in get_columns('accounts_usuario'):
    print(f"{col[0]}: {col[1]}")
