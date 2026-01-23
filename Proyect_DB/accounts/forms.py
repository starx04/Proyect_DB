from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Usuario, Candidato, ExperienciaLaboral, Documento

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('email', 'username', 'tipo_usuario')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'tipo_usuario': forms.Select(attrs={'class': 'form-control'}),
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email o Usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))


class CandidatoPerfilForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['titulo_profesional', 'resumen_perfil', 'telefono', 'salario_esperado']

class ExperienciaForm(forms.ModelForm):
    class Meta:
        model = ExperienciaLaboral
        fields = ['empresa', 'cargo', 'fecha_inicio', 'fecha_fin', 'descripcion']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }
        
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre_archivo', 'url_archivo']
        widgets = {
            'nombre_archivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Mi CV Actual', 'required': 'required'}),
            'url_archivo': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf', 'required': 'required'}),
        }