import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps

for model in apps.get_app_config('jobs').get_models():
    print(f"Model: {model.__name__}, Table: {model._meta.db_table}, Managed: {model._meta.managed}")
