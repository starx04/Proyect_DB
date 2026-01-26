from django import forms
from .models import Empresa, OfertaEmpleo, OfertaHabilidad

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = [
            'nombre_empresa', 'descripcion', 'sector', 'ciudad', 
            'direccion_detalle', 'sitio_web', 'telefono', 'logo_url'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe brevemente a tu empresa...'}),
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'sector': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Tecnología, Finanzas...'}),
            'ciudad': forms.Select(attrs={'class': 'form-select'}),
            'direccion_detalle': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'logo_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL de la imagen de tu logo'}),
        }

class OfertaEmpleoForm(forms.ModelForm):
    class Meta:
        model = OfertaEmpleo
        fields = [
            'titulo', 'categoria', 'ciudad', 'descripcion', 
            'tipo_contrato', 'modalidad', 'salario_min', 'salario_max', 
            'fecha_expiracion', 'estado'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Desarrollador Python Senior'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'ciudad': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detalla las funciones y requisitos...'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
            'modalidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Híbrido, Remoto, Presencial'}),
            'salario_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'salario_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            # Clave: type='date' activa el calendario
            'fecha_expiracion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class OfertaHabilidadForm(forms.ModelForm):
    class Meta:
        model = OfertaHabilidad
        # CORREGIDO: Usamos 'nombre' y 'nivel' (texto libre) en lugar de 'habilidad' y 'nivel_requerido'
        fields = ['nombre', 'nivel', 'es_obligatorio']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Dominio de Inglés, Python, Trabajo en equipo...'
            }),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'es_obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left: 0;'}),
        }