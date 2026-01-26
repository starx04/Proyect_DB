import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print(f"Database Engine: {connection.settings_dict['ENGINE']}")
print(f"Database Name: {connection.settings_dict['NAME']}")
print(f"Database User: {connection.settings_dict['USER']}")
print(f"Database Host: {connection.settings_dict['HOST']}")
print(f"Database Port: {connection.settings_dict['PORT']}")

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        row = cursor.fetchone()
        print(f"Connection successful: {row}")
except Exception as e:
    print(f"Connection failed: {e}")
