import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import Usuario

try:
    # Try to create a dummy user
    u = Usuario.objects.create(username='test_perms', email='test_perms@example.com', tipo_usuario='candidato')
    print(f"Successfully created user: {u.username}")
    u.delete()
    print("Successfully deleted user")
except Exception as e:
    print(f"Failed to create/delete user: {e}")
