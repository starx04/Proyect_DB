from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

"""
APLICATIVO: BOLSA DE EMPLEO (Consolidado)
Todos los modelos del sistema unificados en una sola app.
Reestructurado para coincidir 100% con el diagrama de base de datos.
"""

# ==================== LOCATIONS: MODELOS DE UBICACIÓN ====================

class Pais(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_iso = models.CharField(max_length=2, help_text="Ej: EC, MX")

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"

    def __str__(self):
        return self.nombre

class Provincia(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name='provincias')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre}, {self.pais.codigo_iso}"

class Ciudad(models.Model):
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name='ciudades')
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Ciudades"

    def __str__(self):
        return f"{self.nombre}, {self.provincia.nombre}"


# ==================== ACCOUNTS: ENUMS ====================

class TipoUsuario(models.TextChoices):
    CANDIDATO = 'candidato', _('Candidato')
    EMPRESA = 'empresa', _('Empresa')
    ADMIN = 'admin', _('Admin')

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


# ==================== ACCOUNTS: TABLA usuarios ====================

class Usuario(AbstractUser):
    """
    Tabla: usuarios
    Campos del diagrama: id, email, password_hash, tipo_usuario, estado, created_at, updated_at
    """
    email = models.EmailField(unique=True, null=False)
    # password_hash → manejado por Django con 'password' field de AbstractUser
    tipo_usuario = models.CharField(max_length=20, choices=TipoUsuario.choices, null=False)
    estado = models.BooleanField(default=True, help_text="true=activo, false=baneado")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'tipo_usuario']

    def __str__(self):
        return self.email


# ==================== ACCOUNTS: TABLA empresas ====================

class Empresa(models.Model):
    """
    Tabla: empresas
    Campos del diagrama: id, usuario_id, nombre_empresa, descripcion, sector, 
                         ciudad_id, direccion_detalle, sitio_web, logo_url, telefono
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='perfil_empresa',
        db_column='usuario_id'
    )
    nombre_empresa = models.CharField(max_length=255, null=False)
    descripcion = models.TextField(null=True, blank=True)
    sector = models.CharField(max_length=100, null=True, blank=True)
    ciudad = models.ForeignKey(
        Ciudad, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='ciudad_id'
    )
    direccion_detalle = models.CharField(max_length=255, null=True, blank=True)
    sitio_web = models.CharField(max_length=255, null=True, blank=True)
    logo_url = models.CharField(max_length=500, null=True, blank=True, help_text="URL al bucket S3 o carpeta media")
    telefono = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'empresas'

    def __str__(self):
        return self.nombre_empresa


# ==================== ACCOUNTS: TABLA candidatos ====================

class Candidato(models.Model):
    """
    Tabla: candidatos
    Incluye: datos personales, perfil profesional, URLs externas
    """
    # FK a usuarios
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_candidato',
        db_column='usuario_id'
    )
    
    # DATOS PERSONALES
    nombre_completo = models.CharField(max_length=255, null=False)
    fecha_nacimiento = models.DateField(null=False, help_text="Para calcular la edad automáticamente")
    genero = models.CharField(max_length=20, choices=Genero.choices, null=True, blank=True)
    numero_identificacion = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Cédula, DNI o Pasaporte")
    foto_perfil_url = models.CharField(max_length=500, null=True, blank=True, help_text="URL a la foto del usuario")
    
    # PERFIL PROFESIONAL
    titulo_profesional = models.CharField(max_length=255, null=True, blank=True, help_text="Ej: Desarrollador Backend Junior")
    resumen_perfil = models.TextField(null=True, blank=True)
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ciudad_id'
    )
    telefono = models.CharField(max_length=50, null=True, blank=True)
    salario_esperado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    disponibilidad = models.CharField(max_length=100, null=True, blank=True)
    
    # URLs EXTERNAS
    linkedin_url = models.CharField(max_length=500, null=True, blank=True)
    github_url = models.CharField(max_length=500, null=True, blank=True)
    portfolio_url = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'candidatos'

    def __str__(self):
        return self.nombre_completo


# ==================== ACCOUNTS: TABLA documentos ====================

class Documento(models.Model):
    """
    Tabla: documentos
    Campos: id, candidato_id, nombre_archivo, url_archivo, tipo_documento, created_at
    """
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.CASCADE,
        related_name='documento',
        db_column='candidato_id'
    )
    nombre_archivo = models.CharField(max_length=255, null=True, blank=True)
    url_archivo = models.FileField(upload_to='documentos/', null=False)
    tipo_documento = models.CharField(max_length=50, null=True, blank=True, help_text="CV, Carta, Certificado")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'documentos'

    def __str__(self):
        return f"{self.tipo_documento} - {self.candidato.nombre_completo}"


# ==================== ACCOUNTS: TABLA experiencia_laboral ====================

class ExperienciaLaboral(models.Model):
    """
    Tabla: experiencia_laboral
    Campos: id, candidato_id, empresa, cargo, fecha_inicio, fecha_fin, trabajo_actual, descripcion
    """
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.CASCADE,
        related_name='experiencia_laboral',
        db_column='candidato_id'
    )
    empresa = models.CharField(max_length=255, null=True, blank=True)
    cargo = models.CharField(max_length=255, null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    trabajo_actual = models.BooleanField(default=False)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'experiencia_laboral'
        verbose_name_plural = "Experiencias Laborales"

    def __str__(self):
        return f"{self.cargo} en {self.empresa}"


# ==================== ACCOUNTS: TABLA educacion ====================

class Educacion(models.Model):
    """
    Tabla: educacion
    Campos: id, candidato_id, institucion, titulo, nivel, fecha_inicio, fecha_fin, estado
    """
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.CASCADE,
        related_name='educacion',
        db_column='candidato_id'
    )
    institucion = models.CharField(max_length=255, null=True, blank=True)
    titulo = models.CharField(max_length=255, null=True, blank=True)
    nivel = models.CharField(max_length=100, null=True, blank=True, help_text="Bachiller, Tercer Nivel, Maestría")
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=50, null=True, blank=True, help_text="En curso, Graduado, Trunco")

    class Meta:
        db_table = 'educacion'
        verbose_name = "Educación"
        verbose_name_plural = "Educación"

    def __str__(self):
        return f"{self.titulo} - {self.institucion}"


# ==================== ACCOUNTS: CATÁLOGOS habilidades, idiomas ====================

class Habilidad(models.Model):
    """
    Tabla: habilidades
    Campos: id, nombre
    """
    nombre = models.CharField(max_length=100, unique=True, help_text="Ej: Java, SQL, Excel")

    class Meta:
        db_table = 'habilidades'
        verbose_name_plural = "Habilidades"

    def __str__(self):
        return self.nombre


class Idioma(models.Model):
    """
    Tabla: idiomas
    Campos: id, nombre
    """
    nombre = models.CharField(max_length=100, unique=True, help_text="Ej: Inglés, Francés")

    class Meta:
        db_table = 'idiomas'

    def __str__(self):
        return self.nombre


# ==================== ACCOUNTS: TABLA PIVOTE candidato_habilidad ====================

class CandidatoHabilidad(models.Model):
    """
    Tabla pivote: candidato_habilidad
    Campos: candidato_id, habilidad_id, nivel
    Constraint: unique (candidato_id, habilidad_id)
    """
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.CASCADE,
        related_name='habilidades',
        db_column='candidato_id'
    )
    habilidad = models.ForeignKey(
        Habilidad,
        on_delete=models.CASCADE,
        db_column='habilidad_id'
    )
    nivel = models.CharField(max_length=20, choices=NivelHabilidad.choices)

    class Meta:
        db_table = 'candidato_habilidad'
        unique_together = ('candidato', 'habilidad')

    def __str__(self):
        return f"{self.candidato.nombre_completo} - {self.habilidad.nombre} ({self.nivel})"


# ==================== ACCOUNTS: TABLA PIVOTE candidato_idioma ====================

class CandidatoIdioma(models.Model):
    """
    Tabla pivote: candidato_idioma
    Campos: candidato_id, idioma_id, nivel
    Constraint: unique (candidato_id, idioma_id)
    """
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.CASCADE,
        related_name='idiomas',
        db_column='candidato_id'
    )
    idioma = models.ForeignKey(
        Idioma,
        on_delete=models.CASCADE,
        db_column='idioma_id'
    )
    nivel = models.CharField(max_length=20, help_text="A1, A2, B1, B2, C1, C2, Nativo")

    class Meta:
        db_table = 'candidato_idioma'
        unique_together = ('candidato', 'idioma')

    def __str__(self):
        return f"{self.candidato.nombre_completo} - {self.idioma.nombre} ({self.nivel})"


# ==================== JOBS: ENUMS ====================

class TipoContrato(models.TextChoices):
    TIEMPO_COMPLETO = 'tiempo_completo', _('Tiempo Completo')
    MEDIO_TIEMPO = 'medio_tiempo', _('Medio Tiempo')
    FREELANCE = 'freelance', _('Freelance')
    PASANTIA = 'pasantia', _('Pasantía')
    TEMPORAL = 'temporal', _('Temporal')
    POR_PROYECTO = 'por_proyecto', _('Por Proyecto')


class EstadoOferta(models.TextChoices):
    BORRADOR = 'borrador', _('Borrador')
    PUBLICADA = 'publicada', _('Publicada')
    PAUSADA = 'pausada', _('Pausada')
    CERRADA = 'cerrada', _('Cerrada')
    EXPIRADA = 'expirada', _('Expirada')


class EstadoPostulacion(models.TextChoices):
    PENDIENTE = 'pendiente', _('Pendiente')
    VISTO = 'visto', _('Visto')
    ENTREVISTA = 'entrevista', _('Entrevista')
    PRUEBA_TECNICA = 'prueba_tecnica', _('Prueba Técnica')
    OFERTA = 'oferta', _('Oferta')
    RECHAZADO = 'rechazado', _('Rechazado')
    CONTRATADO = 'contratado', _('Contratado')
    RETIRADO = 'retirado', _('Retirado')


# ==================== JOBS: TABLA categorias ====================

class Categoria(models.Model):
    """
    Tabla: categorias
    Campos: id, nombre, descripcion
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return self.nombre


# ==================== JOBS: TABLA ofertas_empleo ====================

class OfertaEmpleo(models.Model):
    """
    Tabla: ofertas_empleo
    Campos: id, empresa_id, categoria_id, ciudad_id, titulo, descripcion, 
            tipo_contrato, modalidad, salario_min, salario_max, 
            fecha_publicacion, fecha_expiracion, estado
    """
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='ofertas',
        db_column='empresa_id'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='categoria_id'
    )
    ciudad = models.ForeignKey(
        Ciudad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ciudad_id'
    )
    titulo = models.CharField(max_length=255, null=False)
    descripcion = models.TextField(null=False)
    tipo_contrato = models.CharField(
        max_length=50,
        choices=TipoContrato.choices,
        default=TipoContrato.TIEMPO_COMPLETO
    )
    modalidad = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Presencial, Remoto, Híbrido"
    )
    salario_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salario_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoOferta.choices,
        default=EstadoOferta.BORRADOR
    )

    class Meta:
        db_table = 'ofertas_empleo'

    def __str__(self):
        return f"{self.titulo} - {self.empresa.nombre_empresa}"


# ==================== JOBS: TABLA postulaciones ====================

class Postulacion(models.Model):
    """
    Tabla: postulaciones
    Campos: id, oferta_id, candidato_id, fecha_postulacion, estado, feedback_empresa, updated_at
    Constraint: unique (oferta_id, candidato_id)
    """
    oferta = models.ForeignKey(
        OfertaEmpleo,
        on_delete=models.CASCADE,
        related_name='postulaciones',
        db_column='oferta_id'
    )
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.CASCADE,
        related_name='postulaciones',
        db_column='candidato_id'
    )
    fecha_postulacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(
        max_length=20,
        choices=EstadoPostulacion.choices,
        default=EstadoPostulacion.PENDIENTE
    )
    feedback_empresa = models.TextField(
        null=True,
        blank=True,
        help_text="Opcional: Feedback al rechazar"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'postulaciones'
        verbose_name_plural = "Postulaciones"
        unique_together = ('oferta', 'candidato')

    def __str__(self):
        return f"{self.candidato.nombre_completo} → {self.oferta.titulo}"


# ==================== JOBS: TABLA PIVOTE oferta_habilidad ====================

class OfertaHabilidad(models.Model):
    """
    Tabla pivote: oferta_habilidad
    Campos: oferta_id, habilidad_id, nivel_requerido, es_obligatorio
    Constraint: unique (oferta_id, habilidad_id)
    """
    oferta = models.ForeignKey(
        OfertaEmpleo,
        on_delete=models.CASCADE,
        related_name='habilidades_requeridas',
        db_column='oferta_id'
    )
    habilidad = models.ForeignKey(
        Habilidad,
        on_delete=models.CASCADE,
        db_column='habilidad_id'
    )
    nivel_requerido = models.CharField(
        max_length=20,
        choices=NivelHabilidad.choices,
        default=NivelHabilidad.BASICO
    )
    es_obligatorio = models.BooleanField(default=True)

    class Meta:
        db_table = 'oferta_habilidad'
        unique_together = ('oferta', 'habilidad')

    def __str__(self):
        return f"{self.oferta.titulo} - {self.habilidad.nombre} ({self.nivel_requerido})"


# ==================== JOBS: TABLA ofertas_guardadas ====================

class OfertasGuardadas(models.Model):
    """
    Tabla: ofertas_guardadas
    Campos: id, candidato_id, oferta_id, created_at
    """
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.CASCADE,
        related_name='ofertas_guardadas',
        db_column='candidato_id'
    )
    oferta = models.ForeignKey(
        OfertaEmpleo,
        on_delete=models.CASCADE,
        db_column='oferta_id'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'ofertas_guardadas'
        verbose_name = "Oferta Guardada"
        verbose_name_plural = "Ofertas Guardadas"

    def __str__(self):
        return f"{self.candidato.nombre_completo} → {self.oferta.titulo}"
