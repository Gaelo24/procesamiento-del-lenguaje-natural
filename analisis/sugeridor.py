# analisis/sugeridor.py

from django.db.models import Sum
from .models import Palabra, Bigrama, Trigrama

def obtener_sugerencias(contexto: tuple, n: int) -> list:
    """
    Busca la palabra siguiente más probable (versión con consulta corregida).
    """
    sugerencias = []

    if n == 2:
        # --- Modelo de Bigramas ---
        palabra_anterior = contexto[-1]
        
        resultado_suma = Palabra.objects.filter(contenido=palabra_anterior).aggregate(total=Sum('frecuencia'))
        conteo_contexto = resultado_suma['total']

        if not conteo_contexto:
            return []

        bigramas_posibles = Bigrama.objects.filter(contenido__0=palabra_anterior)
        #extr,b/s

        for bigrama in bigramas_posibles:
            palabra_sugerida = bigrama.contenido[1]
            probabilidad = bigrama.frecuencia / conteo_contexto
            sugerencias.append((palabra_sugerida, probabilidad))

    elif n == 3:
        # ---  Trigramas ---
        resultado_suma = Bigrama.objects.filter(contenido=list(contexto)).aggregate(total=Sum('frecuencia'))
        conteo_contexto = resultado_suma['total']

        if not conteo_contexto:
            return []
        
        trigramas_posibles = Trigrama.objects.filter(
            contenido__0=contexto[0],
            contenido__1=contexto[1]
        )
        
        for trigrama in trigramas_posibles:
            palabra_sugerida = trigrama.contenido[2]
            probabilidad = trigrama.frecuencia / conteo_contexto
            sugerencias.append((palabra_sugerida, probabilidad))

    sugerencias.sort(key=lambda item: item[1], reverse=True)
    return sugerencias[:3]