from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

"""
APLICATIVO: JOBS (Ofertas y Postulaciones)

Descripción:
Este módulo es el núcleo del sistema de empleo. Gestiona la publicación de vacantes por parte de las empresas
y el proceso de postulación de los candidatos. Controla el ciclo de vida completo de una oferta.

Modelos:
1. Categoria: Clasificación de las ofertas de empleo.
2. OfertaEmpleo: La vacante publicada con sus detalles, requisitos y estado.
3. Postulacion: Registro de la aplicación de un candidato a una oferta específica.
4. OfertaHabilidad: Habilidades requeridas para una oferta (pivote).
5. OfertasGuardadas: Lista de deseos de candidatos para ofertas de interés.
"""

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

class NivelHabilidad(models.TextChoices):
    BASICO = 'basico', _('Básico')
    INTERMEDIO = 'intermedio', _('Intermedio')
    AVANZADO = 'avanzado', _('Avanzado')
    EXPERTO = 'experto', _('Experto')


# --- MODELOS EXTERNOS
class Ciudad(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    class Meta:
        db_table = 'ciudades'
        managed = False

class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=255)
    class Meta:
        db_table = 'usuarios'
        managed = False

class Habilidad(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    class Meta:
        db_table = 'habilidades'
        managed = False

class Candidato(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    nombre_completo = models.CharField(max_length=255)
    class Meta:
        db_table = 'candidatos'
        managed = False


# ---  MODELOS (INTEGRANTE 3) ---

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'categorias'
        managed = False # Usa la tabla existente

    def __str__(self):
        return self.nombre

class Empresa(models.Model):
    """
    Integrante 3.
    """
    id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, db_column='usuario_id')
    nombre_empresa = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    sector = models.CharField(max_length=255, null=True, blank=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True, db_column='ciudad_id')
    direccion_detalle = models.CharField(max_length=255, null=True, blank=True)
    sitio_web = models.CharField(max_length=255, null=True, blank=True)
    logo_url = models.CharField(max_length=255, null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'empresas'
        managed = False

    def __str__(self):
        return self.nombre_empresa

class OfertaEmpleo(models.Model):
    id = models.AutoField(primary_key=True)
  
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='ofertas', db_column='empresa_id')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, db_column='categoria_id')
    ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, null=True, blank=True, db_column='ciudad_id')
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo_contrato = models.CharField(max_length=50, choices=TipoContrato.choices, default=TipoContrato.TIEMPO_COMPLETO)
    modalidad = models.CharField(max_length=100, blank=True, null=True, help_text="Presencial, Remoto, Híbrido")
    salario_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salario_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=EstadoOferta.choices, default=EstadoOferta.BORRADOR)

    class Meta:
        db_table = 'ofertas_empleo'
        managed = False

    def __str__(self):
        return f"{self.titulo} - {self.empresa.nombre_empresa}"

class OfertaHabilidad(models.Model):
    id = models.AutoField(primary_key=True)
    oferta = models.ForeignKey(OfertaEmpleo, on_delete=models.CASCADE, related_name='habilidades_requeridas', db_column='oferta_id')
   
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE, db_column='habilidad_id')
    nivel_requerido = models.CharField(
        max_length=20, 
        choices=NivelHabilidad.choices,
        default=NivelHabilidad.BASICO
    )
    es_obligatorio = models.BooleanField(default=True)

    class Meta:
        db_table = 'oferta_habilidad'
        managed = False
        unique_together = ('oferta', 'habilidad')

class Postulacion(models.Model):
    id = models.AutoField(primary_key=True)
    oferta = models.ForeignKey(OfertaEmpleo, on_delete=models.CASCADE, related_name='postulaciones', db_column='oferta_id')
    # Cambiado 'accounts.Candidato' a 'Candidato' local
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='postulaciones', db_column='candidato_id')
    fecha_postulacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=20, choices=EstadoPostulacion.choices, default=EstadoPostulacion.PENDIENTE)
    feedback_empresa = models.TextField(blank=True, null=True, help_text="Opcional: Feedback al rechazar")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'postulaciones'
        managed = False
        unique_together = ('oferta', 'candidato')
        verbose_name_plural = "Postulaciones"

    def __str__(self):
        return f"{self.candidato.nombre_completo} -> {self.oferta.titulo}"

class OfertasGuardadas(models.Model):
    id = models.AutoField(primary_key=True)
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE, related_name='ofertas_guardadas', db_column='candidato_id')
    oferta = models.ForeignKey(OfertaEmpleo, on_delete=models.CASCADE, db_column='oferta_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ofertas_guardadas'
        managed = False
        verbose_name = "Oferta Guardada"
        verbose_name_plural = "Ofertas Guardadas"