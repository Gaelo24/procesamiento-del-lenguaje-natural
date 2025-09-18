from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from pathlib import Path
from io import BytesIO
from wordcloud import WordCloud
from django.http import HttpResponse

# Asegúrate de que todos los modelos y funciones estén importados
from .forms import TextoAnalizadoForm
from .models import TextoAnalizado, Palabra, Bigrama, Trigrama
from .preprocesamiento import dividir_texto, generar_bigramas, generar_trigramas, contar_palabras, limpiar_tokens

def cargar_texto(request):
    """
    Vista final para subir un archivo, analizarlo (unigramas, bigramas, trigramas)
    y guardar todos los resultados en la base de datos.
    """
    if request.method == "POST":
        formulario = TextoAnalizadoForm(request.POST, request.FILES)
        if formulario.is_valid():
            # Primero, crea el objeto principal para tener una referencia
            texto_obj = formulario.save()

            try:
                # Lee el contenido del archivo una sola vez
                contenido = Path(texto_obj.archivo.path).read_text(encoding="utf-8", errors="ignore")
                tokens = dividir_texto(contenido)

                # --- ANÁLISIS Y GUARDADO DE DATOS ---

                # 1. Procesa y guarda UNIGRAMAS
                frecuencia_unigramas = contar_palabras(tokens)
                if frecuencia_unigramas:
                    Palabra.objects.bulk_create([
                        Palabra(texto=texto_obj, contenido=palabra, frecuencia=freq)
                        for palabra, freq in frecuencia_unigramas.items()
                    ])

                # 2. Procesa y guarda BIGRAMAS
                bigramas = generar_bigramas(tokens)
                frecuencia_bigramas = contar_palabras(bigramas)
                if frecuencia_bigramas:
                    Bigrama.objects.bulk_create([
                        Bigrama(texto=texto_obj, contenido=list(bigrama), frecuencia=freq)
                        for bigrama, freq in frecuencia_bigramas.items()
                    ])

                # 3. Procesa y guarda TRIGRAMAS
                trigramas = generar_trigramas(tokens)
                frecuencia_trigramas = contar_palabras(trigramas)
                if frecuencia_trigramas:
                    Trigrama.objects.bulk_create([
                        Trigrama(texto=texto_obj, contenido=list(trigrama), frecuencia=freq)
                        for trigrama, freq in frecuencia_trigramas.items()
                    ])
                
                # 4. Genera la nube de palabras (opcional)
                tokens_limpios = limpiar_tokens(contenido)
                if tokens_limpios:
                    texto_limpio = " ".join(tokens_limpios)
                    wc = WordCloud(width=800, height=400, background_color="white", collocations=False).generate(texto_limpio)
                    buf = BytesIO()
                    wc.to_image().save(buf, format="PNG")
                    filename = f"nube_{texto_obj.id}.png"
                    texto_obj.nube_imagen.save(filename, ContentFile(buf.getvalue()), save=True)

            except Exception as e:
                # Si algo falla, imprime el error en la consola para saber qué pasó
                print(f"❌ ERROR CRÍTICO DURANTE EL PROCESAMİENTO: {e}")

            return redirect("listar_textos")
    else:
        formulario = TextoAnalizadoForm()

    return render(request, "analisis/subir.html", {"form": formulario})

def listar_textos(request):
    """Muestra todos los textos subidos en orden descendente."""
    datos = TextoAnalizado.objects.order_by("-fecha_subida")
    return render(request, "analisis/lista.html", {"textos": datos})

def home(request):
    return HttpResponse("Bienvenido al Sistema de PLN")