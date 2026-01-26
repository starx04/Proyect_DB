from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CandidatoPerfilForm, ExperienciaForm, DocumentoForm
from .models import Empresa, Candidato
from django.contrib.auth.decorators import login_required

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
                return redirect('jobs:dashboard_empresa')
            return redirect('wizard_perfil', paso=1)
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Hola de nuevo, {user.username}')
            
            # Redirección inteligente
            if user.tipo_usuario == 'empresa':
                return redirect('jobs:dashboard_empresa')
            return redirect('dashboard_candidato')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


#### PARTE KARLA ####

@login_required
def perfil_candidato_step(request):
    # Obtenemos el perfil del usuario logueado
    candidato = request.user.perfil_candidato
    
    if request.method == 'POST':
        form = CandidatoPerfilForm(request.POST, instance=candidato)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Perfil actualizado!")
            return redirect('dashboard_candidato')
    else:
        form = CandidatoPerfilForm(instance=candidato)
    
    return render(request, 'accounts/perfil_form.html', {'form': form})

@login_required
def dashboard_candidato(request):
    candidato = request.user.perfil_candidato
    # Obtenemos sus datos relacionados
    experiencias = candidato.experiencia_laboral.all().order_by('-fecha_inicio')
    educacion = candidato.educacion.all().order_by('-fecha_inicio')
    
    # Datos nuevos
    postulaciones = candidato.postulaciones.select_related('oferta', 'oferta__empresa').order_by('-fecha_postulacion')[:5]
    ofertas_guardadas = candidato.ofertas_guardadas.select_related('oferta', 'oferta__empresa').order_by('-created_at')[:5]
    habilidades = candidato.habilidades.select_related('habilidad').all()
    idiomas = candidato.idiomas.select_related('idioma').all()
    
    # Stats
    stats = {
        'postulaciones_activas': candidato.postulaciones.exclude(estado='rechazado').count(),
        'entrevistas': candidato.postulaciones.filter(estado='entrevista').count(),
        'guardadas': candidato.ofertas_guardadas.count()
    }
    
    return render(request, 'candidatoPerfil/dashboard.html', {
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
    from .models import Habilidad, CandidatoHabilidad, Documento
    from .forms import HabilidadForm # Import needed forms

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
        template = 'candidatoPerfil/paso1_personales.html'
    
    elif paso == 2:
        form = ExperienciaForm() 
        template = 'candidatoPerfil/paso2_experiencia.html'
        
    elif paso == 3:
        # Habilidades (Nuevo paso)
        form = HabilidadForm()
        template = 'candidatoPerfil/paso3_habilidades.html'

    elif paso == 4:
        # Archivos (Antes Paso 3)
        # Buscamos el último CV para editarlo si existe
        documento = candidato.documento.filter(tipo_documento="CV").last()
        form = DocumentoForm(instance=documento)
        template = 'candidatoPerfil/paso4_archivos.html' # Changed name
    else:
        return redirect('dashboard_candidato')

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
             return redirect('wizard_perfil', paso=3)
        
        if paso == 3 and request.POST.get('tiene_habilidades') == 'no':
             return redirect('wizard_perfil', paso=4)

        if paso == 4 and request.POST.get('tiene_cv') == 'no':
             # Si dice que no tiene CV, pero ya existía uno, ¿lo borramos? O solo terminamos
             # Por ahora, terminamos
             messages.info(request, "Registro finalizado.")
             return redirect('dashboard_candidato')


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
                
                # En este paso, tal vez queremos permitir agregar MAS habilidades.
                # Por simplicidad ahora, guardamos una y pasamos al siguiente o recargamos?
                # El usuario pedía "Agregar", así que idealmente debería quedarse en el mismo paso o tener un botón "Agregar otra".
                # Vamos a asumir "Guardar y Continuar" para el flujo básico del wizard.
                # Si quiere agregar más, puede volver.
                
                return redirect('wizard_perfil', paso=4)

            # GUARDADO PASO 4 (ARCHIVOS)
            if paso == 4:
                obj = form.save(commit=False)
                obj.candidato = candidato
                obj.tipo_documento = "CV"
                obj.save()
                messages.success(request, "¡Perfil Completado!")
                return redirect('dashboard_candidato')

            # GUARDADO PASOS 1 y 2
            obj = form.save(commit=False)
            if paso == 1:
                obj.usuario = request.user
            elif paso == 2:
                obj.candidato = candidato
            
            obj.save()
            
            # Redirecciones
            if paso == 1: return redirect('wizard_perfil', paso=2)
            if paso == 2: return redirect('wizard_perfil', paso=3)

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
            return redirect('dashboard_candidato')
    else:
        form = DocumentoForm()
    
    return render(request, 'accounts/subir_cv.html', {'form': form})