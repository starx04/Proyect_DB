from django.urls import path, include
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('perfil/subir-cv/', views.subir_cv_view, name='subir_cv'),
    path('perfil/<int:paso>/', views.wizard_perfil, name='wizard_perfil'),
    path('dashboard/', views.dashboard_candidato, name='dashboard_candidato'),
    path('perfil/editar/', views.perfil_candidato_step, name='editar_perfil'),
]

