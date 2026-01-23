from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Pais, Provincia, Ciudad

def load_cities(request):
    """
    AJAX Endpoint: Retorna ciudades dado un provincia_id.
    """
    provincia_id = request.GET.get('provincia_id')
    cities = Ciudad.objects.filter(provincia_id=provincia_id).order_by('nombre')
    return JsonResponse(list(cities.values('id', 'nombre')), safe=False)

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_locations_view(request):
    """
    Vista simple para que el admin visualice ubicaciones.
    (En una implementación completa, aquí irían formularios CRUD).
    """
    paises = Pais.objects.all().prefetch_related('provincias__ciudades')
    return render(request, 'locations/admin_panel.html', {'paises': paises})
