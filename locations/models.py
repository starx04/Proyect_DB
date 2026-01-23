from django.db import models

"""
APLICATIVO: LOCATIONS (Ubicación)

Descripción:
Este módulo gestiona la información geográfica necesaria para el sistema. 
Permite normalizar las ubicaciones de empresas y candidatos mediante una estructura jerárquica.

Modelos:
1. Pais: Representa un país con su código ISO.
2. Provincia: División administrativa de primer nivel de un país.
3. Ciudad: Ciudad o localidad específica dentro de una provincia.
"""

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
