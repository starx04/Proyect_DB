from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import FileExtensionValidator
from .models import (
    Usuario, Candidato, ExperienciaLaboral, Documento, CandidatoHabilidad, 
    CandidatoIdioma, Idioma, Empresa, OfertaEmpleo, OfertaHabilidad
)

# ==================== AUTENTICACIÓN ====================

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


# ==================== CANDIDATOS ====================

class CandidatoPerfilForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['nombre_completo', 'numero_identificacion', 'titulo_profesional', 'resumen_perfil', 'telefono', 'salario_esperado']
        widgets = {
             'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
             'numero_identificacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1712345678'}),
             'titulo_profesional': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Desarrollador Backend'}),
             'telefono': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel', 'maxlength': '10'}),
             'salario_esperado': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
        }

    def clean_numero_identificacion(self):
        cedula = self.cleaned_data.get('numero_identificacion')
        if not cedula:
            return cedula
        
        # Validación de cédula ecuatoriana (10 dígitos)
        if len(cedula) != 10 or not cedula.isdigit():
            raise forms.ValidationError("La cédula debe tener 10 dígitos numéricos.")
        
        provincia = int(cedula[0:2])
        if provincia < 0 or (provincia > 24 and provincia != 30):
            raise forms.ValidationError("Código de provincia fuera de rango.")
        
        d3 = int(cedula[2])
        if d3 > 6:
            raise forms.ValidationError("Identificación inválida.")
        
        # Algoritmo de validación de checksum
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        for i in range(9):
            valor = int(cedula[i]) * coeficientes[i]
            if valor >= 10:
                valor -= 9
            suma += valor
        
        verificador = int(cedula[9])
        digito_v = (10 - (suma % 10)) if (suma % 10) != 0 else 0
        
        if digito_v != verificador:
            raise forms.ValidationError("El número de cédula es incorrecto.")
            
        return cedula

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

# FORM SIMPLIFICADO: solo campos del diagrama
class ExperienciaForm(forms.ModelForm):
    class Meta:
        model = ExperienciaLaboral
        fields = ['empresa', 'cargo', 'fecha_inicio', 'fecha_fin', 'trabajo_actual', 'descripcion']
        widgets = {
            'empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la empresa'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu cargo o puesto'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe tus funciones principales...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Todos opcionales según el diagrama
        for field in self.fields:
            self.fields[field].required = False

# FORM SIMPLIFICADO: solo 'nivel' según el diagrama
class HabilidadForm(forms.ModelForm):
    nombre_habilidad = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Python, Liderazgo, Excel'})
    )

    class Meta:
        model = CandidatoHabilidad
        fields = ['nivel']
        widgets = {
            'nivel': forms.Select(attrs={'class': 'form-select'}),
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
    
    def __init__(self, *args, **kwargs):
        super(DocumentoForm, self).__init__(*args, **kwargs)
        self.fields['nombre_archivo'].required = False
        self.fields['url_archivo'].required = False

class IdiomaForm(forms.ModelForm):
    nombre_idioma = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Inglés, Francés, Alemán'})
    )

    class Meta:
        model = CandidatoIdioma
        fields = ['nivel']
        widgets = {
            'nivel': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('A1', 'A1 - Acceso'),
                ('A2', 'A2 - Plataforma'),
                ('B1', 'B1 - Umbral'),
                ('B2', 'B2 - Avanzado'),
                ('C1', 'C1 - Dominio eficaz'),
                ('C2', 'C2 - Competencia técnica'),
                ('nativo', 'Lengua Materna / Nativo'),
            ]),
        }


# ==================== EMPRESAS ====================

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            'nombre_empresa', 'descripcion', 'sector', 'ciudad', 
            'direccion_detalle', 'sitio_web', 'telefono', 'logo_url'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'sector': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.Select(attrs={'class': 'form-control'}),
            'direccion_detalle': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'logo_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL de tu logo'}),
        }


# ==================== OFERTAS DE EMPLEO ====================

class OfertaEmpleoForm(forms.ModelForm):
    class Meta:
        model = OfertaEmpleo
        fields = [
            'titulo', 'categoria', 'ciudad', 'descripcion', 
            'tipo_contrato', 'modalidad', 'salario_min', 'salario_max', 
            'fecha_expiracion', 'estado'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'ciudad': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-control'}),
            'modalidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Híbrido 2 días'}),
            'salario_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salario_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_expiracion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

class OfertaHabilidadForm(forms.ModelForm):
    class Meta:
        model = OfertaHabilidad
        fields = ['habilidad', 'nivel_requerido', 'es_obligatorio']
        widgets = {
            'habilidad': forms.Select(attrs={'class': 'form-control'}),
            'nivel_requerido': forms.Select(attrs={'class': 'form-control'}),
            'es_obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
