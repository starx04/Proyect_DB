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
            'sector': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('tecnologia', 'Tecnología e Informática'),
                ('salud', 'Salud y Bienestar'),
                ('educacion', 'Educación y Formación'),
                ('finanzas', 'Banca y Finanzas'),
                ('comercio', 'Comercio y Ventas'),
                ('construccion', 'Construcción e Inmobiliaria'),
                ('turismo', 'Turismo y Gastronomía'),
                ('otro', 'Otro Sector'),
            ]),
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
            'modalidad': forms.Select(attrs={'class': 'form-control'}),
            'salario_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salario_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_expiracion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        salario_min = cleaned_data.get('salario_min')
        salario_max = cleaned_data.get('salario_max')

        if salario_min and salario_max and salario_min > salario_max:
            raise forms.ValidationError(
                "El salario mínimo no puede ser mayor que el salario máximo."
            )
        return cleaned_data

class OfertaHabilidadForm(forms.ModelForm):
    class Meta:
        model = OfertaHabilidad
        fields = ['habilidad', 'nivel_requerido', 'es_obligatorio']
        widgets = {
            'habilidad': forms.Select(attrs={'class': 'form-control'}),
            'nivel_requerido': forms.Select(attrs={'class': 'form-control'}),
            'es_obligatorio': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }