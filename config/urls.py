"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

# Vista Home con Redirección por Rol
def home_view(request):
    if request.user.is_authenticated:
        if request.user.tipo_usuario == 'empresa':
            return redirect('jobs:dashboard_empresa')
        elif request.user.tipo_usuario == 'candidato':
            return redirect('dashboard_candidato')
    return render(request, 'home.html')

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Apps de otros integrantes
    path('accounts/', include('accounts.urls')),
    path('locations/', include('locations.urls')),

    # --- MÓDULO (Integrante 3) ---
    
    path('jobs/', include('jobs.urls')),

    # Página de inicio
    path('', home_view, name='home'),
]

# Configuración para servir archivos multimedia (imágenes, PDFs) en modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)