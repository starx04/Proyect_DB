from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, CandidatoPerfilForm, 
    ExperienciaForm, DocumentoForm, HabilidadForm, EmpresaForm, 
    OfertaEmpleoForm, OfertaHabilidadForm
)
from .models import (
    Empresa, Candidato, OfertaEmpleo, OfertaHabilidad, Postulacion, 
    EstadoPostulacion, OfertasGuardadas, Habilidad, CandidatoHabilidad, 
    Documento, Pais, Provincia, Ciudad
)

"""
BOLSA DE EMPLEO - VISTAS CONSOLIDADAS
Todas las vistas del sistema unificadas en un solo archivo.
"""

# ==================== HOME ====================

def home_view(request):
    """Vista principal con redirección por rol"""
    if request.user.is_authenticated:
        if request.user.tipo_usuario == 'empresa':
            return redirect('bolsa_empleo:dashboard_empresa')
        elif request.user.tipo_usuario == 'candidato':
            return redirect('bolsa_empleo:dashboard_candidato')
    return render(request, 'home.html')

# ==================== AUTENTICACIÓN ====================

def registro_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear perfil asociado según el tipo de usuario
            if user.tipo_usuario == 'empresa':
                Empresa.objects.create(usuario=user, nombre_empresa=f"Empresa {user.username}")
            elif user.tipo_usuario == 'candidato':
                Candidato.objects.create(usuario=user, nombre_completo=user.username, fecha_nacimiento='2000-01-01') # Default date, user updates later
            
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}!')
            
            # Redirección según tipo
            if user.tipo_usuario == 'empresa':
                return redirect('bolsa_empleo:dashboard_empresa')
            return redirect('bolsa_empleo:wizard_perfil', paso=1)
    else:
        form = CustomUserCreationForm()
    return render(request, 'bolsa_empleo/auth/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Hola de nuevo, {user.username}')
            
            # Redirección inteligente
            if user.tipo_usuario == 'empresa':
                return redirect('bolsa_empleo:dashboard_empresa')
            return redirect('bolsa_empleo:dashboard_candidato')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'bolsa_empleo/auth/login.html', {'form': form})


# ==================== CANDIDATOS ====================

@login_required
def perfil_candidato_step(request):
    # Obtenemos el perfil del usuario logueado
    candidato = request.user.perfil_candidato
    
    if request.method == 'POST':
        form = CandidatoPerfilForm(request.POST, instance=candidato)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Perfil actualizado!")
            return redirect('bolsa_empleo:dashboard_candidato')
    else:
        form = CandidatoPerfilForm(instance=candidato)
    
    return render(request, 'bolsa_empleo/candidato/perfil_form.html', {'form': form})

@login_required
def dashboard_candidato(request):
    candidato = request.user.perfil_candidato

    experiencias = candidato.experiencia_laboral.all().order_by('-fecha_inicio')
    educacion = candidato.educacion.all().order_by('-fecha_inicio')
    
    postulaciones = candidato.postulaciones.select_related(
        'oferta', 'oferta__empresa'
    ).order_by('-fecha_postulacion')[:5]

    ofertas_guardadas = candidato.ofertas_guardadas.select_related(
        'oferta', 'oferta__empresa'
    ).order_by('-created_at')[:5]

    habilidades = candidato.habilidades.select_related('habilidad').all()
    idiomas = candidato.idiomas.select_related('idioma').all()
    
    stats = {
        'postulaciones_activas': candidato.postulaciones.exclude(estado='rechazado').count(),
        'entrevistas': candidato.postulaciones.filter(estado='entrevista').count(),
        'guardadas': candidato.ofertas_guardadas.count()
    }
    
    return render(request, 'bolsa_empleo/candidato/dashboard.html', {
        'candidato': candidato,
        'experiencias': experiencias,
        'educacion': educacion,
        'postulaciones': postulaciones,
        'ofertas_guardadas': ofertas_guardadas,
        'habilidades': habilidades,
        'idiomas': idiomas,
        'stats': stats
    })


@login_required
def wizard_perfil(request, paso=1):
    # 1. Obtener el candidato
    try:
        candidato = Candidato.objects.get(usuario=request.user)
    except Candidato.DoesNotExist:
        candidato = Candidato.objects.create(
            usuario=request.user, 
            nombre_completo=request.user.username, 
            fecha_nacimiento='2000-01-01'
        )

    # --- LÓGICA DE FORMULARIOS (GET) ---
    if paso == 1:
        form = CandidatoPerfilForm(instance=candidato)
        template = 'bolsa_empleo/candidato/wizard/paso1_personales.html'
    
    elif paso == 2:
        form = ExperienciaForm() 
        template = 'bolsa_empleo/candidato/wizard/paso2_experiencia.html'
        
    elif paso == 3:
        # Habilidades (Nuevo paso)
        form = HabilidadForm()
        template = 'bolsa_empleo/candidato/wizard/paso3_habilidades.html'

    elif paso == 4:
        # Archivos (Antes Paso 3)
        # Buscamos el último CV para editarlo si existe
        documento = candidato.documento.filter(tipo_documento="CV").last()
        form = DocumentoForm(instance=documento)
        template = 'bolsa_empleo/candidato/wizard/paso4_archivos.html'
    else:
        return redirect('bolsa_empleo:dashboard_candidato')

    # --- PROCESAMIENTO DE DATOS (POST) ---
    if request.method == 'POST':
        if paso == 1:
            form = CandidatoPerfilForm(request.POST, instance=candidato)
        elif paso == 2:
            form = ExperienciaForm(request.POST)
        elif paso == 3:
            form = HabilidadForm(request.POST)
        elif paso == 4:
            documento = candidato.documento.filter(tipo_documento="CV").last()
            form = DocumentoForm(request.POST, request.FILES, instance=documento)

        # VALIDACIONES ESPECIFICAS POR PASO
        
        # 1. Validar si saltan el paso (Solo para pasos opcionales: 2 y 3 y 4)
        if paso == 2 and request.POST.get('tiene_experiencia') == 'no':
             return redirect('bolsa_empleo:wizard_perfil', paso=3)
        
        if paso == 3 and request.POST.get('tiene_habilidades') == 'no':
             return redirect('bolsa_empleo:wizard_perfil', paso=4)

        if paso == 4 and request.POST.get('tiene_cv') == 'no':
             # Si dice que no tiene CV, pero ya existía uno, ¿lo borramos? O solo terminamos
             # Por ahora, terminamos
             messages.info(request, "Registro finalizado.")
             return redirect('bolsa_empleo:dashboard_candidato')


        # 2. Guardar Formulario
        if form.is_valid():
            
            # GUARDADO PASO 3 (HABILIDADES)
            if paso == 3:
                nombre = form.cleaned_data['nombre_habilidad']
                # Buscar o crear la habilidad en el catálogo
                habilidad_obj, created = Habilidad.objects.get_or_create(nombre__iexact=nombre, defaults={'nombre': nombre})
                
                # Crear la relación (evitar duplicados)
                if not CandidatoHabilidad.objects.filter(candidato=candidato, habilidad=habilidad_obj).exists():
                    candi_hab = form.save(commit=False)
                    candi_hab.candidato = candidato
                    candi_hab.habilidad = habilidad_obj
                    candi_hab.save()
                
                return redirect('bolsa_empleo:wizard_perfil', paso=4)

            # GUARDADO PASO 4 (ARCHIVOS)
            if paso == 4:
                obj = form.save(commit=False)
                obj.candidato = candidato
                obj.tipo_documento = "CV"
                obj.save()
                messages.success(request, "¡Perfil Completado!")
                return redirect('bolsa_empleo:dashboard_candidato')

            # GUARDADO PASOS 1 y 2
            obj = form.save(commit=False)
            if paso == 1:
                obj.usuario = request.user
            elif paso == 2:
                obj.candidato = candidato
            
            obj.save()
            
            # Redirecciones
            if paso == 1: return redirect('bolsa_empleo:wizard_perfil', paso=2)
            if paso == 2: return redirect('bolsa_empleo:wizard_perfil', paso=3)

    # Contexto
    context = {
        'form': form, 
        'paso': paso,
        'candidato': candidato,
    }
    
    # Datos extra para visualización
    if paso == 2: context['experiencias'] = candidato.experiencia_laboral.all()
    if paso == 3: context['habilidades'] = candidato.habilidades.all() # Mostrar las que va agregando
    
    return render(request, template, context)



@login_required
def subir_cv_view(request):
    candidato = request.user.perfil_candidato
    
    if request.method == 'POST':
        # ¡Importante! request.FILES es lo que recibe el archivo PDF
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.candidato = candidato
            documento.tipo_documento = "CV" # Marcamos que es su hoja de vida
            documento.save()
            messages.success(request, "¡Tu CV se ha subido con éxito!")
            return redirect('bolsa_empleo:dashboard_candidato')
    else:
        form = DocumentoForm()
    
    return render(request, 'bolsa_empleo/candidato/subir_cv.html', {'form': form})

@login_required
def perfil_publico_candidato(request, candidato_id):
    """Vista detallada del perfil de un candidato para que las empresas lo evalúen."""
    candidato = get_object_or_404(Candidato, id=candidato_id)
    
    # Obtenemos sus datos relacionados
    experiencias = candidato.experiencia_laboral.all().order_by('-fecha_inicio')
    educacion = candidato.educacion.all().order_by('-fecha_inicio')
    habilidades = candidato.habilidades.select_related('habilidad').all()
    idiomas = candidato.idiomas.select_related('idioma').all()
    documentos = candidato.documento.all()

    return render(request, 'bolsa_empleo/candidato/perfil_publico.html', {
        'candidato': candidato,
        'experiencias': experiencias,
        'educacion': educacion,
        'habilidades': habilidades,
        'idiomas': idiomas,
        'documentos': documentos
    })


# ==================== EMPRESAS ====================

@login_required
def dashboard_empresa(request):
    """Panel principal de la empresa con sus ofertas."""
    try:
        empresa = Empresa.objects.get(usuario=request.user)
    except Empresa.DoesNotExist:
        return redirect('bolsa_empleo:editar_perfil_empresa')

    ofertas = OfertaEmpleo.objects.filter(empresa=empresa).order_by('-fecha_publicacion')
    # Añadimos el conteo de postulantes
    for oferta in ofertas:
        oferta.num_postulantes = oferta.postulaciones.count()
        
    return render(request, 'bolsa_empleo/empresa/dashboard_empresa.html', {'ofertas': ofertas, 'empresa': empresa})

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
            nueva_empresa.usuario = request.user
            nueva_empresa.save()
            messages.success(request, 'Perfil de empresa actualizado correctamente.')
            return redirect('bolsa_empleo:dashboard_empresa')
    else:
        form = EmpresaForm(instance=empresa)

    return render(request, 'bolsa_empleo/empresa/editar_empresa.html', {'form': form})

def perfil_publico_empresa(request, empresa_id):
    """Vista pública para que los candidatos vean la info de la empresa."""
    empresa = get_object_or_404(Empresa, id=empresa_id)
    ofertas_activas = OfertaEmpleo.objects.filter(empresa=empresa, estado='publicada')
    return render(request, 'bolsa_empleo/empresa/perfil_publico.html', {'empresa': empresa, 'ofertas': ofertas_activas})


# ==================== OFERTAS DE EMPLEO ====================

@login_required
def crear_oferta(request):
    try:
        empresa = Empresa.objects.get(usuario=request.user)
    except Empresa.DoesNotExist:
        messages.error(request, 'Debes completar tu perfil de empresa antes de publicar ofertas.')
        return redirect('bolsa_empleo:editar_perfil_empresa')

    if request.method == 'POST':
        form = OfertaEmpleoForm(request.POST)
        if form.is_valid():
            oferta = form.save(commit=False)
            oferta.empresa = empresa
            oferta.save()
            messages.success(request, 'Oferta creada. Ahora añade las habilidades requeridas.')
            return redirect('bolsa_empleo:gestionar_habilidades', oferta_id=oferta.id)
    else:
        form = OfertaEmpleoForm()

    return render(request, 'bolsa_empleo/ofertas/crear_oferta.html', {'form': form, 'titulo': 'Crear Nueva Oferta'})

@login_required
def editar_oferta(request, oferta_id):
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)

    if request.method == 'POST':
        form = OfertaEmpleoForm(request.POST, instance=oferta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Oferta actualizada correctamente.')
            return redirect('bolsa_empleo:dashboard_empresa')
    else:
        form = OfertaEmpleoForm(instance=oferta)

    return render(request, 'bolsa_empleo/ofertas/crear_oferta.html', {'form': form, 'titulo': 'Editar Oferta'})

@login_required
def eliminar_oferta(request, oferta_id):
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)
    
    if request.method == 'POST':
        oferta.delete()
        messages.success(request, 'Oferta eliminada.')
    
    return redirect('bolsa_empleo:dashboard_empresa')

@login_required
def gestionar_habilidades(request, oferta_id):
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)
    habilidades_asignadas = oferta.habilidades_requeridas.all()

    if request.method == 'POST':
        form = OfertaHabilidadForm(request.POST)
        if form.is_valid():
            habilidad_input = form.cleaned_data['habilidad']
            if OfertaHabilidad.objects.filter(oferta=oferta, habilidad=habilidad_input).exists():
                messages.warning(request, 'Esta habilidad ya está asignada a la oferta.')
            else:
                nueva_relacion = form.save(commit=False)
                nueva_relacion.oferta = oferta
                nueva_relacion.save()
                messages.success(request, 'Habilidad agregada.')
            return redirect('bolsa_empleo:gestionar_habilidades', oferta_id=oferta.id)
    else:
        form = OfertaHabilidadForm()

    return render(request, 'bolsa_empleo/ofertas/gestionar_habilidades.html', {
        'oferta': oferta,
        'habilidades': habilidades_asignadas,
        'form': form
    })

@login_required
def eliminar_habilidad(request, habilidad_id):
    habilidad_rel = get_object_or_404(OfertaHabilidad, id=habilidad_id)
    if habilidad_rel.oferta.empresa.usuario != request.user:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect('bolsa_empleo:dashboard_empresa')
    
    oferta_id = habilidad_rel.oferta.id
    habilidad_rel.delete()
    messages.success(request, 'Habilidad eliminada de la oferta.')
    return redirect('bolsa_empleo:gestionar_habilidades', oferta_id=oferta_id)

def lista_ofertas(request):
    """Listado público de ofertas."""
    ofertas = OfertaEmpleo.objects.filter(estado='publicada').order_by('-fecha_publicacion')
    return render(request, 'bolsa_empleo/ofertas/lista_ofertas.html', {'ofertas': ofertas})

def detallar_oferta(request, oferta_id):
    """Detalle de la oferta y botón de postulación."""
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id)
    ya_postulado = False
    
    if request.user.is_authenticated and request.user.tipo_usuario == 'candidato':
        ya_postulado = Postulacion.objects.filter(oferta=oferta, candidato=request.user.perfil_candidato).exists()
        
    return render(request, 'bolsa_empleo/ofertas/detallar_oferta.html', {
        'oferta': oferta,
        'ya_postulado': ya_postulado
    })


# ==================== POSTULACIONES ====================

@login_required
def postularse(request, oferta_id):
    if request.user.tipo_usuario != 'candidato':
        messages.error(request, 'Solo los candidatos pueden postularse.')
        return redirect('home')
        
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id)
    candidato = request.user.perfil_candidato
    
    postulacion, created = Postulacion.objects.get_or_create(oferta=oferta, candidato=candidato)
    if created:
        messages.success(request, f'¡Te has postulado con éxito a "{oferta.titulo}"!')
    else:
        messages.warning(request, 'Ya te habías postulado a esta oferta.')
        
    return redirect('bolsa_empleo:detallar_oferta', oferta_id=oferta.id)

@login_required
def guardar_oferta(request, oferta_id):
    if request.user.tipo_usuario != 'candidato':
        messages.error(request, 'Acción no permitida.')
        return redirect('home')

    candidato = request.user.perfil_candidato
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id)

    OfertasGuardadas.objects.get_or_create(candidato=candidato, oferta=oferta)
    messages.success(request, 'Oferta guardada.')
    return redirect('bolsa_empleo:dashboard_candidato')

@login_required
def mis_postulaciones(request):
    if request.user.tipo_usuario != 'candidato':
        messages.error(request, 'Acceso no autorizado.')
        return redirect('home')

    candidato = request.user.perfil_candidato
    postulaciones = Postulacion.objects.filter(candidato=candidato).select_related('oferta', 'oferta__empresa')

    return render(request, 'bolsa_empleo/postulaciones/mis_postulaciones.html', {'postulaciones': postulaciones})

@login_required
def ver_postulantes(request, oferta_id):
    empresa = get_object_or_404(Empresa, usuario=request.user)
    oferta = get_object_or_404(OfertaEmpleo, id=oferta_id, empresa=empresa)
    postulaciones = oferta.postulaciones.select_related('candidato', 'candidato__usuario').order_by('-fecha_postulacion')
    
    return render(request, 'bolsa_empleo/postulaciones/ver_postulantes.html', {
        'oferta': oferta,
        'postulaciones': postulaciones,
        'estados': EstadoPostulacion.choices
    })

@login_required
def cambiar_estado_postulacion(request, postulacion_id):
    postulacion = get_object_or_404(Postulacion, id=postulacion_id)
    if postulacion.oferta.empresa.usuario != request.user:
        messages.error(request, 'No tienes permiso para gestionar esta postulación.')
        return redirect('bolsa_empleo:dashboard_empresa')
        
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(EstadoPostulacion.choices):
        postulacion.estado = nuevo_estado
        postulacion.save()
        messages.success(request, 'Estado actualizado correctamente.')
    
    return redirect('bolsa_empleo:ver_postulantes', oferta_id=postulacion.oferta.id)


# ==================== UBICACIÓN ====================

def load_cities(request):
    """
    AJAX Endpoint: Retorna ciudades dado un provincia_id.
    """
    provincia_id = request.GET.get('provincia_id')
    cities = Ciudad.objects.filter(provincia_id=provincia_id).order_by('nombre')
    return JsonResponse(list(cities.values('id', 'nombre')), safe=False)
