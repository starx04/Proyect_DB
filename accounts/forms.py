from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import FileExtensionValidator
from .models import Usuario, Candidato, ExperienciaLaboral, Documento, CandidatoHabilidad

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
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))


class CandidatoPerfilForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['titulo_profesional', 'resumen_perfil', 'telefono', 'salario_esperado']
        widgets = {
             'titulo_profesional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Desarrollador Backend'}),
             'telefono': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'maxlength': '10'}),
             'salario_esperado': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

    def clean_titulo_profesional(self):
        titulo = self.cleaned_data.get('titulo_profesional')
        if titulo:
            import re
            if not re.match(r'^[a-zA-Z\s]+$', titulo):
                raise forms.ValidationError("El título solo puede contener letras y espacios.")
        return titulo

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
             import re
             if not re.match(r'^\d+$', telefono):
                 raise forms.ValidationError("Solo se permiten números.")
             
             if len(telefono) != 10:
                 raise forms.ValidationError("El teléfono debe tener exactamente 10 dígitos.")
                 
        return telefono

    def clean_salario_esperado(self):
        salario = self.cleaned_data.get('salario_esperado')
        if salario is not None and salario < 0:
            raise forms.ValidationError("El salario no puede ser negativo.")
        return salario

class ExperienciaForm(forms.ModelForm):
    class Meta:
        model = ExperienciaLaboral
        fields = [
            'empresa', 'cargo', 'fecha_inicio', 'fecha_fin', 'trabajo_actual', 'ubicacion', 'descripcion',
            'logros', 'tecnologias', 'personas_cargo', 'descripcion_empresa',
            'motivo_salida', 'tipo_contrato', 'proyectos_destacados'
        ]
        widgets = {
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la empresa'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu cargo o puesto'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad, País'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe tus funciones principales...'}),
            
            'logros': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ej: Aumento de ventas en un 15%'}),
            'tecnologias': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Python, SAP, Scrum'}),
            'personas_cargo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'descripcion_empresa': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Breve descripción del sector y tamaño'}),
            
            'motivo_salida': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo_contrato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Indefinido, Freelance'}),
            'proyectos_destacados': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 1. Campos Obligatorios (Indispensables)
        self.fields['empresa'].required = True
        self.fields['cargo'].required = True
        self.fields['fecha_inicio'].required = True
        self.fields['ubicacion'].required = True
        self.fields['descripcion'].required = True
        
        # El resto son opcionales
        self.fields['fecha_fin'].required = False
        self.fields['trabajo_actual'].required = False
        self.fields['logros'].required = False
        self.fields['tecnologias'].required = False
        self.fields['personas_cargo'].required = False
        self.fields['descripcion_empresa'].required = False
        self.fields['motivo_salida'].required = False
        self.fields['tipo_contrato'].required = False
        self.fields['proyectos_destacados'].required = False

class HabilidadForm(forms.ModelForm):
    # Campo auxiliar para ingresar el nombre
    nombre_habilidad = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Python, Liderazgo, Excel'})
    )

    class Meta:
        model = CandidatoHabilidad
        fields = ['nivel', 'anios_experiencia', 'contexto_uso']
        widgets = {
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'anios_experiencia': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': '0'}),
            'contexto_uso': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej: Proyecto eCommerce, Empresa ABC...'}),
        }
        
class DocumentoForm(forms.ModelForm):
    url_archivo = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        help_text="Solo archivos PDF o Word (.doc, .docx)"
    )

    class Meta:
        model = Documento
        fields = ['nombre_archivo', 'url_archivo']
        widgets = {
             'nombre_archivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: CV 2024'}),
        }
    
    # Hacemos que los campos no sean obligatorios (se validan en la vista si el usuario dice SI)
    def __init__(self, *args, **kwargs):
        super(DocumentoForm, self).__init__(*args, **kwargs)
        self.fields['nombre_archivo'].required = False
        self.fields['url_archivo'].required = False