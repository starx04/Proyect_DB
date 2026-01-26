from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Empresa, OfertaEmpleo, OfertaHabilidad, Postulacion, OfertasGuardadas, EstadoPostulacion
from .forms import EmpresaForm, OfertaEmpleoForm, OfertaHabilidadForm
from accounts.models import Candidato

# ==========================================
# 1. GESTIÓN DE EMPRESA (Perfil y Dashboard)
# ==========================================

@login_required
def dashboard_empresa(request):
    """Panel principal de la empresa con sus ofertas publicadas."""
    # Validación: Solo empresas pueden entrar aquí
    if request.user.tipo_usuario != 'empresa' and not request.user.is_superuser:
        messages.error(request, "Acceso restringido solo para empresas.")
        return redirect('home')

    try:
        empresa = Empresa.objects.get(usuario=request.user)
    except Empresa.DoesNotExist:
        # Si el usuario es empresa pero no tiene perfil, lo mandamos a crear uno
        return redirect('jobs:editar_perfil_empresa')

    ofertas = OfertaEmpleo.objects.filter(empresa=empresa).order_by('-fecha_publicacion')
    return render(request, 'jobs/dashboard_empresa.html', {'ofertas': ofertas, 'empresa': empresa})

@login_required
def editar_perfil_empresa(request):
    """Permite a la empresa editar sus datos públicos (logo, descripción, etc)."""
    if request.user.tipo_usuario != 'empresa' and not request.user.is_superuser:
        return redirect('home')

    try:
        empresa = Empresa.objects.get(usuario=request.user)
    except Empresa.DoesNotExist:
        empresa = None # Caso: es la primera vez que entra

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
    # Solo mostramos ofertas que estén 'publicadas'
    ofertas_activas = OfertaEmpleo.objects.filter(empresa=empresa, estado='publicada')
    return render(request, 'jobs/perfil_publico.html', {'empresa': empresa, 'ofertas': ofertas_activas})


# ==========================================
# 2. GESTIÓN DE OFERTAS (CRUD)
# ==========================================

@login_required
def crear_oferta(request):
    """Paso 1: Crear la información básica de la oferta."""
    # Validación: Verificar que tiene perfil de empresa creado
    try:
        empresa = Empresa.objects.get(usuario=request.user)
    except Empresa.DoesNotExist:
        messages.error(request, 'Debes completar tu perfil de empresa antes de publicar ofertas.')
        return redirect('jobs:editar_perfil_empresa')

    if request.method == 'POST':
        form = OfertaEmpleoForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.empresa = empresa # Asignamos la oferta a la empresa actual
            oferta.save()
            messages.success(request, 'Oferta creada. Ahora añade las habilidades requeridas.')
            # Redirigimos al Paso 2: Agregar Habilidades
            return redirect('jobs:gestionar_habilidades', oferta_id=oferta.id)
    else:
        form = OfertaEmpleoForm()

    return render(request, 'jobs/crear_oferta.html', {'form': form, 'titulo': 'Crear Nueva Oferta'})

@login_required
def editar_oferta(request, oferta_id):
    """Permite editar una oferta existente."""
    empresa = get_object_or_404(Empresa, usuario=request.user)
    # Seguridad: Aseguramos que la oferta pertenezca a esta empresa
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
    """Elimina una oferta (Solo si pertenece a la empresa)."""
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)
    
    if request.method == 'POST':
        oferta.delete()
        messages.success(request, 'Oferta eliminada.')
    
    return redirect('jobs:dashboard_empresa')


# ==========================================
# 3. GESTIÓN DE HABILIDADES (Requisitos)
# ==========================================

@login_required
def gestionar_habilidades(request, oferta_id):
    """Paso 2: Agregar requisitos de texto libre a la oferta."""
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)
    
    habilidades_asignadas = oferta.habilidades_requeridas.all()

    if request.method == 'POST':
        form = OfertaHabilidadForm(request.POST)
        if form.is_valid():
            # Limpiamos el texto (quitamos espacios extra)
            nombre_input = form.cleaned_data['nombre'].strip()
            
            # Validación simple: Evitar duplicados exactos en la misma oferta
            if OfertaHabilidad.objects.filter(oferta=oferta, nombre__iexact=nombre_input).exists():
                messages.warning(request, f"El requisito '{nombre_input}' ya está en la lista.")
            else:
                nuevo_requisito = form.save(commit=False)
                nuevo_requisito.oferta = oferta
                nuevo_requisito.save()
                messages.success(request, 'Requisito agregado correctamente.')
            
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
    """Elimina una habilidad de una oferta."""
    habilidad_rel = get_object_or_404(OfertaHabilidad, id=habilidad_id)
    
    # Seguridad: verificar que la oferta pertenece a la empresa actual
    if habilidad_rel.oferta.empresa.usuario != request.user:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('jobs:dashboard_empresa')
    
    oferta_id = habilidad_rel.oferta.id
    habilidad_rel.delete()
    messages.success(request, 'Habilidad eliminada de la oferta.')
    return redirect('jobs:gestionar_habilidades', oferta_id=oferta_id)


# ==========================================
# 4. INTERACCIÓN CANDIDATO - OFERTA
# ==========================================

@login_required
def postular_oferta(request, oferta_id):
    """Permite a un candidato postularse a una oferta con validaciones estrictas."""
    # Validación 1: Rol
    if request.user.tipo_usuario != 'candidato':
        messages.error(request, 'Solo los candidatos pueden postular.')
        return redirect('home')

    candidato = get_object_or_404(Candidato, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id)

    # Validación 2: Estado de la oferta
    if oferta.estado != 'publicada':
        messages.error(request, 'Esta oferta no está disponible para postulación.')
        return redirect('home')

    # Validación 3: Duplicados (Chequeo explícito)
    if Postulacion.objects.filter(candidato=candidato, oferta=oferta).exists():
        messages.warning(request, 'Ya te has postulado a esta oferta previamente.')
        return redirect('jobs:mis_postulaciones')

    # Crear Postulación
    Postulacion.objects.create(candidato=candidato, oferta=oferta)
    messages.success(request, '¡Postulación enviada exitosamente!')
    return redirect('jobs:mis_postulaciones')

@login_required
def guardar_oferta(request, oferta_id):
    """Permite a un candidato guardar una oferta en favoritos."""
    if request.user.tipo_usuario != 'candidato':
        messages.error(request, 'Acción no permitida.')
        return redirect('home')

    candidato = get_object_or_404(Candidato, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id)

    # get_or_create evita duplicados automáticamente
    OfertasGuardadas.objects.get_or_create(
        candidato=candidato,
        oferta=oferta
    )

    messages.success(request, 'Oferta guardada en favoritos.')
    return redirect('home') 

@login_required
def mis_postulaciones(request):
    """Muestra al candidato todas sus postulaciones."""
    if request.user.tipo_usuario != 'candidato':
        messages.error(request, 'Acceso no autorizado.')
        return redirect('home')

    candidato = get_object_or_404(Candidato, usuario=request.user)
    postulaciones = Postulacion.objects.filter(candidato=candidato).select_related('oferta', 'oferta__empresa')

    return render(request, 'jobs/mis_postulaciones.html', {
        'postulaciones': postulaciones
    })


# ==========================================
# 5. GESTIÓN DE APLICANTES (Vista Empresa)
# ==========================================

@login_required
def gestion_aplicantes(request, oferta_id):
    """La empresa ve quién se ha postulado a su oferta y cambia estados."""
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)

    # Procesar cambio de estado (Si se envió el formulario)
    if request.method == 'POST':
        postulacion_id = request.POST.get('postulacion_id')
        nuevo_estado = request.POST.get('estado')

        postulacion = get_object_or_404(
            Postulacion,
            id=postulacion_id,
            oferta=oferta  # Seguridad: solo postulaciones de ESTA oferta
        )

        postulacion.estado = nuevo_estado
        postulacion.save()

        messages.success(request, 'Estado de la postulación actualizado correctamente.')
        return redirect('jobs:gestion_aplicantes', oferta_id=oferta.id)

    # Mostrar lista de postulantes
    postulaciones = Postulacion.objects.filter(oferta=oferta).select_related('candidato', 'candidato__usuario')

    return render(request, 'jobs/gestion_aplicantes.html', {
        'oferta': oferta,
        'postulaciones': postulaciones,
        'estados': EstadoPostulacion.choices
    })