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
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control'}),
            'sector': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.Select(attrs={'class': 'form-control'}),
            'direccion_detalle': forms.TextInput(attrs={'class': 'form-control'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'logo_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL de tu logo'}),
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