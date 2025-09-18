from django.db import models
from django.db.models import Sum

class TextoAnalizado(models.Model):
    titulo = models.CharField(max_length=200)
    archivo = models.FileField(upload_to='textos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)
    tokens_json = models.JSONField(null=True, blank=True)
    nube_imagen = models.ImageField(upload_to='nubes/', null=True, blank=True)

    def __str__(self):
        return self.titulo

    # MÉTODOS CORREGIDOS: usan 'self.palabras'
    def palabras_unicas(self):
        return self.palabras.count()

    def total_palabras(self):
        resultado = self.palabras.aggregate(total=Sum('frecuencia'))
        return resultado['total'] or 0

class Palabra(models.Model): # Este es tu modelo de Unigramas
    texto = models.ForeignKey(TextoAnalizado, on_delete=models.CASCADE, related_name='palabras')
    contenido = models.CharField(max_length=255)
    frecuencia = models.PositiveIntegerField()

    def __str__(self):
        return f"'{self.contenido}' ({self.frecuencia} veces)"

class Bigrama(models.Model): # NUEVO MODELO
    texto = models.ForeignKey(TextoAnalizado, on_delete=models.CASCADE, related_name='bigramas')
    contenido = models.JSONField() # Guarda la tupla, ej: ["el", "perro"]
    frecuencia = models.PositiveIntegerField()

    def __str__(self):
        return f"'{' '.join(self.contenido)}' ({self.frecuencia} veces)"

class Trigrama(models.Model): # NUEVO MODELO
    texto = models.ForeignKey(TextoAnalizado, on_delete=models.CASCADE, related_name='trigramas')
    contenido = models.JSONField() # Guarda la tupla, ej: ["el", "perro", "come"]
    frecuencia = models.PositiveIntegerField()

    def __str__(self):
        return f"'{' '.join(self.contenido)}' ({self.frecuencia} veces)"
