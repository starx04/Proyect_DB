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
            return redirect('home')
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
            return redirect('home')
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
    experiencias = candidato.experiencia_laboral.all()
    educacion = candidato.educacion.all()
    
    return render(request, 'candidatoPerfil/dashboard.html', {
        'candidato': candidato,
        'experiencias': experiencias,
        'educacion': educacion
    })

@login_required
def wizard_perfil(request, paso=1):
    candidato = request.user.perfil_candidato
    if paso > 1 and not candidato.titulo_profesional:
        messages.warning(request, "Primero debes completar tus datos personales.")
        return redirect('wizard_perfil', paso=1)
    
    if paso == 1:
        form = CandidatoPerfilForm(instance=candidato)
        template = 'candidatoPerfil/paso1_personales.html'
    elif paso == 2:
        form = ExperienciaForm()
        template = 'candidatoPerfil/paso2_experiencia.html'
    elif paso == 3: # NUEVO PASO PARA EL CV
        form = DocumentoForm()
        template = 'candidatoPerfil/paso3_subir_cv.html'
    else:
        return redirect('dashboard_candidato')

    if request.method == 'POST':
        if paso == 1:
            form = CandidatoPerfilForm(request.POST, instance=candidato)
        elif paso == 2:
            form = ExperienciaForm(request.POST)
        elif paso == 3:
            # ¡IMPORTANTE! request.FILES es necesario para el PDF
            form = DocumentoForm(request.POST, request.FILES)
            
        if form.is_valid():
            obj = form.save(commit=False)
            if paso == 2 or paso == 3:
                obj.candidato = candidato
            if paso == 3:
                obj.tipo_documento = "CV"
            obj.save()
            
            # Si es el último paso, al dashboard; si no, al siguiente paso
            if paso == 3:
                messages.success(request, "¡Perfil completo y CV subido!")
                return redirect('dashboard_candidato')
            return redirect('wizard_perfil', paso=paso+1)
    if paso == 3:
        obj.tipo_documento = "CV"
        obj.save()
        messages.success(request, "¡Perfil completo y CV subido!")
        # Este nombre debe existir en urls.py
        return redirect('dashboard_candidato')

    return render(request, template, {'form': form, 'paso': paso})

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