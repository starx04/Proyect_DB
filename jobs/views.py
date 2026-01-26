from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Empresa, OfertaEmpleo, OfertaHabilidad, Postulacion, EstadoPostulacion
from .forms import EmpresaForm, OfertaEmpleoForm, OfertaHabilidadForm
from .models import Postulacion, OfertasGuardadas, EstadoPostulacion
from accounts.models import Candidato


# --- GESTIÓN DE EMPRESA ---

@login_required
def dashboard_empresa(request):
    """Panel principal de la empresa con sus ofertas."""
    try:
        empresa = Empresa.objects.get(usuario=request.user)
    except Empresa.DoesNotExist:
        # Si el usuario es empresa pero no tiene perfil, lo mandamos a crear uno
        return redirect('jobs:editar_perfil_empresa')

    ofertas = OfertaEmpleo.objects.filter(empresa=empresa).order_by('-fecha_publicacion')
    
    # Inyectar el número de postulantes en cada oferta
    for oferta in ofertas:
        oferta.num_postulantes = oferta.postulaciones.count()
        
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
            return redirect('jobs:dashboard_empresa')
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
        return redirect('jobs:editar_perfil_empresa')

    if request.method == 'POST':
        form = OfertaEmpleoForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.empresa = empresa
            oferta.save()
            messages.success(request, 'Oferta creada. Ahora añade las habilidades requeridas.')
            return redirect('jobs:gestionar_habilidades', oferta_id=oferta.id)
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
            return redirect('jobs:dashboard_empresa')
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
    
    return redirect('jobs:dashboard_empresa')


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
            return redirect('jobs:gestionar_habilidades', oferta_id=oferta.id)
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
    if habilidad_rel.oferta.empresa.usuario != request.user:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('jobs:dashboard_empresa')
    
    oferta_id = habilidad_rel.oferta.id
    habilidad_rel.delete()
    messages.success(request, 'Habilidad eliminada de la oferta.')
<<<<<<< HEAD
    return redirect('jobs:gestionar_habilidades', oferta_id=oferta_id)


# --- FLUJO DE CANDIDATO ---

def lista_ofertas(request):
    """Listado público de ofertas para los candidatos."""
    ofertas = OfertaEmpleo.objects.filter(estado='publicada').order_by('-fecha_publicacion')
    return render(request, 'jobs/lista_ofertas.html', {'ofertas': ofertas})

def detallar_oferta(request, oferta_id):
    """Detalle de la oferta y botón de postulación."""
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id)
    ya_postulado = False
    
    if request.user.is_authenticated and request.user.tipo_usuario == 'candidato':
        ya_postulado = Postulacion.objects.filter(oferta=oferta, candidato=request.user.perfil_candidato).exists()
        
    return render(request, 'jobs/detallar_oferta.html', {
        'oferta': oferta,
        'ya_postulado': ya_postulado
    })

@login_required
def postularse(request, oferta_id):
    """Crea una nueva postulación para el candidato logueado."""
    if request.user.tipo_usuario != 'candidato':
        messages.error(request, 'Solo los candidatos pueden postularse a ofertas.')
        return redirect('home')
        
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id)
    candidato = request.user.perfil_candidato
    
    postulacion, created = Postulacion.objects.get_or_create(oferta=oferta, candidato=candidato)
    
    if created:
        messages.success(request, f'¡Te has postulado con éxito a "{oferta.titulo}"!')
    else:
        messages.warning(request, 'Ya te habías postulado a esta oferta anteriormente.')
        
    return redirect('jobs:detallar_oferta', oferta_id=oferta.id)


# --- GESTIÓN DE POSTULANTES ---

@login_required
def ver_postulantes(request, oferta_id):
    """Permite a la empresa ver quiénes aplicaron a su oferta."""
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)
    postulaciones = oferta.postulaciones.select_related('candidato__usuario').order_by('-fecha_postulacion')
    
    return render(request, 'jobs/ver_postulantes.html', {
        'oferta': oferta,
=======
    return redirect('gestionar_habilidades', oferta_id=oferta_id)

# Vistas postulaciones
@login_required
def postular_oferta(request, oferta_id):
    # Verificar que el usuario sea candidato
    if request.user.tipo_usuario != 'candidato':
        messages.error(request, 'Solo los candidatos pueden postular.')
        return redirect('home')

    candidato = get_object_or_404(Candidato, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, estado='publicada')

    postulacion, created = Postulacion.objects.get_or_create(
        candidato=candidato,
        oferta=oferta
    )

    if created:
        messages.success(request, 'Postulación realizada correctamente.')
    else:
        messages.info(request, 'Ya te has postulado a esta oferta.')

    return redirect('mis_postulaciones')

@login_required
def guardar_oferta(request, oferta_id):
    if request.user.tipo_usuario != 'candidato':
        messages.error(request, 'Acción no permitida.')
        return redirect('home')

    candidato = get_object_or_404(Candidato, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id)

    OfertasGuardadas.objects.get_or_create(
        candidato=candidato,
        oferta=oferta
    )

    messages.success(request, 'Oferta guardada.')
    return redirect('ofertas_guardadas')

@login_required
def mis_postulaciones(request):
    if request.user.tipo_usuario != 'candidato':
        messages.error(request, 'Acceso no autorizado.')
        return redirect('home')

    candidato = get_object_or_404(Candidato, usuario=request.user)
    postulaciones = Postulacion.objects.filter(
        candidato=candidato
    ).select_related('oferta', 'oferta__empresa')

    return render(request, 'jobs/mis_postulaciones.html', {
>>>>>>> 2b27c6f510334cc8c614c95eaf1e687186ad6c70
        'postulaciones': postulaciones
    })

@login_required
<<<<<<< HEAD
def cambiar_estado_postulacion(request, postulacion_id):
    """Permite aprobar o rechazar una postulación."""
    postulacion = get_object_or_404(Postulacion, id=postulacion_id)
    
    if postulacion.oferta.empresa.usuario != request.user:
        messages.error(request, 'No tienes permiso para gestionar esta postulación.')
        return redirect('jobs:dashboard_empresa')
        
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(EstadoPostulacion.choices):
        postulacion.estado = nuevo_estado
        postulacion.save()
        messages.success(request, f'Estado de la postulación actualizado correctamente.')
    
    return redirect('jobs:ver_postulantes', oferta_id=postulacion.oferta.id)
=======
def gestion_aplicantes(request, oferta_id):
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)

    # cambiar estado
    if request.method == 'POST':
        postulacion_id = request.POST.get('postulacion_id')
        nuevo_estado = request.POST.get('estado')

        postulacion = get_object_or_404(
            Postulacion,
            id=postulacion_id,
            oferta=oferta  # seguridad: solo postulaciones de ESTA oferta
        )

        postulacion.estado = nuevo_estado
        postulacion.save()

        messages.success(request, 'Estado de la postulación actualizado correctamente.')
        return redirect('jobs:gestion_aplicantes', oferta_id=oferta.id)

    # mostrar postulaciones
    postulaciones = Postulacion.objects.filter(
        oferta=oferta
    ).select_related('candidato', 'candidato__usuario')

    return render(request, 'jobs/gestion_aplicantes.html', {
        'oferta': oferta,
        'postulaciones': postulaciones,
        'estados': EstadoPostulacion.choices
    })
>>>>>>> 2b27c6f510334cc8c614c95eaf1e687186ad6c70
