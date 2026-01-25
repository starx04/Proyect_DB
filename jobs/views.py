from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Empresa, OfertaEmpleo, OfertaHabilidad
from .forms import EmpresaForm, OfertaEmpleoForm, OfertaHabilidadForm

# --- GESTIÓN DE EMPRESA ---

@login_required
def dashboard_empresa(request):
    """Panel principal de la empresa con sus ofertas."""
    try:
        empresa = Empresa.objects.get(usuario=request.user)
    except Empresa.DoesNotExist:
        # Si el usuario es empresa pero no tiene perfil, lo mandamos a crear uno
        return redirect('editar_perfil_empresa')

    ofertas = OfertaEmpleo.objects.filter(empresa=empresa).order_by('-fecha_publicacion')
    return render(request, 'jobs/dashboard_empresa.html', {'ofertas': ofertas, 'empresa': empresa})

@login_required
def editar_perfil_empresa(request):
    """Permite a la empresa editar sus datos públicos."""
    try:
        empresa = Empresa.objects.get(usuario=request.user)
    except Empresa.DoesNotExist:
        empresa = None # Caso nuevo usuario empresa

    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            nueva_empresa = form.save(commit=False)
            nueva_empresa.usuario = request.user # Asignamos el usuario conectado
            nueva_empresa.save()
            messages.success(request, 'Perfil de empresa actualizado correctamente.')
            return redirect('dashboard_empresa')
    else:
        form = EmpresaForm(instance=empresa)

    return render(request, 'jobs/editar_empresa.html', {'form': form})

def perfil_publico_empresa(request, empresa_id):
    """Vista pública para que los candidatos vean la info de la empresa."""
    empresa = get_object_or_404(Empresa, id=empresa_id)
    ofertas_activas = OfertaEmpleo.objects.filter(empresa=empresa, estado='publicada')
    return render(request, 'jobs/perfil_publico.html', {'empresa': empresa, 'ofertas': ofertas_activas})


# --- GESTIÓN DE OFERTAS ---

@login_required
def crear_oferta(request):
    try:
        empresa = Empresa.objects.get(usuario=request.user)
    except Empresa.DoesNotExist:
        messages.error(request, 'Debes completar tu perfil de empresa antes de publicar ofertas.')
        return redirect('editar_perfil_empresa')

    if request.method == 'POST':
        form = OfertaEmpleoForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.empresa = empresa
            oferta.save()
            messages.success(request, 'Oferta creada. Ahora añade las habilidades requeridas.')
            return redirect('gestionar_habilidades', oferta_id=oferta.id)
    else:
        form = OfertaEmpleoForm()

    return render(request, 'jobs/crear_oferta.html', {'form': form, 'titulo': 'Crear Nueva Oferta'})

@login_required
def editar_oferta(request, oferta_id):
    # Aseguramos que la oferta pertenezca a la empresa logueada
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)

    if request.method == 'POST':
        form = OfertaEmpleoForm(request.POST, instance=oferta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Oferta actualizada correctamente.')
            return redirect('dashboard_empresa')
    else:
        form = OfertaEmpleoForm(instance=oferta)

    return render(request, 'jobs/crear_oferta.html', {'form': form, 'titulo': 'Editar Oferta'})

@login_required
def eliminar_oferta(request, oferta_id):
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)
    
    if request.method == 'POST':
        oferta.delete()
        messages.success(request, 'Oferta eliminada.')
    
    return redirect('dashboard_empresa')


# --- GESTIÓN DE HABILIDADES DE LA OFERTA ---

@login_required
def gestionar_habilidades(request, oferta_id):
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)
    habilidades_asignadas = oferta.habilidades_requeridas.all()

    if request.method == 'POST':
        form = OfertaHabilidadForm(request.POST)
        if form.is_valid():
            # Verificar si ya existe esa habilidad en la oferta para no duplicar
            habilidad_input = form.cleaned_data['habilidad']
            if OfertaHabilidad.objects.filter(oferta=oferta, habilidad=habilidad_input).exists():
                messages.warning(request, 'Esta habilidad ya está asignada a la oferta.')
            else:
                nueva_relacion = form.save(commit=False)
                nueva_relacion.oferta = oferta
                nueva_relacion.save()
                messages.success(request, 'Habilidad agregada.')
            return redirect('gestionar_habilidades', oferta_id=oferta.id)
    else:
        form = OfertaHabilidadForm()

    return render(request, 'jobs/gestionar_habilidades.html', {
        'oferta': oferta,
        'habilidades': habilidades_asignadas,
        'form': form
    })

@login_required
def eliminar_habilidad(request, habilidad_id):
    habilidad_rel = get_object_or_404(OfertaHabilidad, id=habilidad_id)
    # Seguridad: verificar que la oferta pertenece a la empresa actual
    if habilidad_rel.oferta.empresa.usuario != request.user:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('dashboard_empresa')
    
    oferta_id = habilidad_rel.oferta.id
    habilidad_rel.delete()
    messages.success(request, 'Habilidad eliminada de la oferta.')
    return redirect('gestionar_habilidades', oferta_id=oferta_id)