from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

"""
APLICATIVO: ACCOUNTS (Usuarios y Perfiles)

Descripción:
Este módulo administra la autenticación y los perfiles de los usuarios del sistema.
Distingue entre candidatos reclutados y empresas que publican ofertas.

Modelos:
1. Usuario: Modelo de usuario personalizado que extiende de AbstractUser.
2. Empresa: Perfil para reclutadores/empresas.
3. Candidato: Perfil para postulantes con datos personales y profesionales.
4. Habilidad / Idioma: Catálogos de competencias.
5. CandidatoHabilidad / CandidatoIdioma: Tablas pivote con niveles.
6. ExperienciaLaboral / Educacion: Historial profesional y académico.
7. Documento: Archivos adjuntos del candidato (CV, cartas, etc).
"""

class TipoUsuario(models.TextChoices):
    CANDIDATO = 'candidato', _('Candidato')
    EMPRESA = 'empresa', _('Empresa')
    ADMIN = 'admin', _('Administrador')

class Genero(models.TextChoices):
    MASCULINO = 'masculino', _('Masculino')
    FEMENINO = 'femenino', _('Femenino')
    OTRO = 'otro', _('Otro')
    PREFIERO_NO_DECIR = 'prefiero_no_decir', _('Prefiero no decir')

class NivelHabilidad(models.TextChoices):
    BASICO = 'basico', _('Básico')
    INTERMEDIO = 'intermedio', _('Intermedio')
    AVANZADO = 'avanzado', _('Avanzado')
    EXPERTO = 'experto', _('Experto')

class Usuario(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    tipo_usuario = models.CharField(max_length=20, choices=TipoUsuario.choices)
    estado = models.BooleanField(default=True, help_text="true=activo, false=baneado")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'tipo_usuario']

    def __str__(self):
        return self.email

class Empresa(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_empresa')
    nombre_empresa = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    sector = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.ForeignKey('locations.Ciudad', on_delete=models.SET_NULL, null=True, blank=True)
    direccion_detalle = models.CharField(max_length=255, blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)
    logo_url = models.CharField(max_length=500, blank=True, null=True, help_text="URL al bucket S3 o carpeta media")
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre_empresa

class Candidato(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_candidato')
    
    # Datos Personales
    nombre_completo = models.CharField(max_length=200)
    fecha_nacimiento = models.DateField(help_text="Para calcular la edad automáticamente")
    genero = models.CharField(max_length=20, choices=Genero.choices, blank=True, null=True)
    numero_identificacion = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Cédula, DNI o Pasaporte")
    foto_perfil_url = models.CharField(max_length=500, blank=True, null=True, help_text="URL a la foto del usuario")
    
    # Perfil Profesional
    titulo_profesional = models.CharField(max_length=200, blank=True, null=True, help_text="Ej: Desarrollador Backend Junior")
    resumen_perfil = models.TextField(blank=True, null=True)
    ciudad = models.ForeignKey('locations.Ciudad', on_delete=models.SET_NULL, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    salario_esperado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    disponibilidad = models.CharField(max_length=100, blank=True, null=True)
    
    # URLs Externas
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.nombre_completo

class Documento(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='documentos')
    nombre_archivo = models.CharField(max_length=255)
    url_archivo = models.CharField(max_length=500)
    tipo_documento = models.CharField(max_length=50, help_text="CV, Carta, Certificado")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_archivo} ({self.candidato.nombre_completo})"

class Habilidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text="Ej: Java, SQL, Excel")

    class Meta:
        verbose_name_plural = "Habilidades"

    def __str__(self):
        return self.nombre

class Idioma(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text="Ej: Inglés, Francés")

    def __str__(self):
        return self.nombre

class CandidatoHabilidad(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='habilidades')
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE)
    nivel = models.CharField(max_length=20, choices=NivelHabilidad.choices)

    class Meta:
        unique_together = ('candidato', 'habilidad')

class CandidatoIdioma(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='idiomas')
    idioma = models.ForeignKey(Idioma, on_delete=models.CASCADE)
    nivel = models.CharField(max_length=20, help_text="A1, A2, B1, B2, C1, C2, Nativo")

    class Meta:
        unique_together = ('candidato', 'idioma')

class ExperienciaLaboral(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='experiencia_laboral')
    empresa = models.CharField(max_length=200)
    cargo = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    trabajo_actual = models.BooleanField(default=False)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Experiencias Laborales"

class Educacion(models.Model):
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='educacion')
    institucion = models.CharField(max_length=200)
    titulo = models.CharField(max_length=200)
    nivel = models.CharField(max_length=100, help_text="Bachiller, Tercer Nivel, Maestría")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=50, help_text="En curso, Graduado, Trunco")

    class Meta:
        verbose_name = "Educación"
        verbose_name_plural = "Educación"
