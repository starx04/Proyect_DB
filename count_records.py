import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps

for model in apps.get_models():
    count = model.objects.count()
    print(f"{model._meta.label}: {count} records")
