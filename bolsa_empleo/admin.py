from django.contrib import admin
from .models import (
    # Locations
    Pais, Provincia, Ciudad,
    # Accounts
    Usuario, Empresa, Candidato, Documento, ExperienciaLaboral, Educacion,
    Habilidad, Idioma, CandidatoHabilidad, CandidatoIdioma,
    # Jobs
    Categoria, OfertaEmpleo, Postulacion, OfertaHabilidad, OfertasGuardadas
)

# Registrar modelos en el admin
admin.site.register(Pais)
admin.site.register(Provincia)
admin.site.register(Ciudad)
admin.site.register(Usuario)
admin.site.register(Empresa)
admin.site.register(Candidato)
admin.site.register(Documento)
admin.site.register(ExperienciaLaboral)
admin.site.register(Educacion)
admin.site.register(Habilidad)
admin.site.register(Idioma)
admin.site.register(CandidatoHabilidad)
admin.site.register(CandidatoIdioma)
admin.site.register(Categoria)
admin.site.register(OfertaEmpleo)
admin.site.register(Postulacion)
admin.site.register(OfertaHabilidad)
admin.site.register(OfertasGuardadas)
