from django.urls import path
from . import views

urlpatterns = [
    path('ajax/load-cities/', views.load_cities, name='ajax_load_cities'),
    path('admin-panel/', views.admin_locations_view, name='admin_locations'),
]
