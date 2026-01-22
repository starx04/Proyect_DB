from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import Empresa, Candidato

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
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.first_name or user.username}!')
            
            # Redirección Inteligente (si venía de otra pag)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
                
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Por favor verifícalos.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})
