import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'accounts_documento'
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"{col[0]}: {col[1]}")
