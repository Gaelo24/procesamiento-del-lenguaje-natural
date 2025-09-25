from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from pathlib import Path
from io import BytesIO
from wordcloud import WordCloud
from django.http import HttpResponse

from .forms import TextoAnalizadoForm
from .models import TextoAnalizado, Palabra, Bigrama, Trigrama
from .preprocesamiento import generar_bigramas, generar_trigramas, contar_palabras, limpiar_tokens, tokenizar
from .sugeridor import obtener_sugerencias



def cargar_texto(request):
    """
    Vista final para subir un archivo, analizarlo (unigramas, bigramas, trigramas)
    y guardar todos los resultados en la base de datos.
    """
    if request.method == "POST":
        formulario = TextoAnalizadoForm(request.POST, request.FILES)
        if formulario.is_valid():
            texto_obj = formulario.save()

            try:
                contenido = Path(texto_obj.archivo.path).read_text(encoding="utf-8", errors="ignore")
                
                # Usamos 'tokenizar' (el nombre correcto)
                tokens = tokenizar(contenido)

                # Procesa y guarda UNIGRAMAS
                frecuencia_unigramas = contar_palabras(tokens)
                if frecuencia_unigramas:
                    Palabra.objects.bulk_create([
                        Palabra(texto=texto_obj, contenido=p, frecuencia=f) for p, f in frecuencia_unigramas.items()
                    ])

                # Procesa y guarda BIGRAMAS
                bigramas = generar_bigramas(tokens)
                frecuencia_bigramas = contar_palabras(bigramas)
                if frecuencia_bigramas:
                    Bigrama.objects.bulk_create([
                        Bigrama(texto=texto_obj, contenido=list(b), frecuencia=f) for b, f in frecuencia_bigramas.items()
                    ])

                # Procesa y guarda TRIGRAMAS
                trigramas = generar_trigramas(tokens)
                frecuencia_trigramas = contar_palabras(trigramas)
                if frecuencia_trigramas:
                    Trigrama.objects.bulk_create([
                        Trigrama(texto=texto_obj, contenido=list(t), frecuencia=f) for t, f in frecuencia_trigramas.items()
                    ])
                
                # Genera la nube de palabras
                tokens_limpios = limpiar_tokens(contenido)
                if tokens_limpios:
                    texto_limpio = " ".join(tokens_limpios)
                    wc = WordCloud(width=800, height=400, background_color="white", collocations=False).generate(texto_limpio)
                    buf = BytesIO()
                    wc.to_image().save(buf, format="PNG")
                    filename = f"nube_{texto_obj.id}.png"
                    texto_obj.nube_imagen.save(filename, ContentFile(buf.getvalue()), save=True)

            except Exception as e:
                print(f"❌ ERROR CRÍTICO DURANTE EL PROCESAMIENTO: {e}")

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

def autocomplementar_view(request):
    context = {}
    
    # Si el usuario envió el formulario (hizo clic en el botón)
    if request.method == 'POST':
        texto_usuario = request.POST.get('texto_usuario', '')
        n = int(request.POST.get('n_grama', 2)) # Obtiene el n=2 o n=3 del <select>
        
        # Guardamos lo que el usuario escribió para mostrarlo de nuevo en la caja
        context['texto_actual'] = texto_usuario
        context['n_actual'] = n

        if texto_usuario:
            # 1. Convertimos el texto del usuario en una lista de palabras (tokens)
            tokens = tokenizar(texto_usuario) 
            
            # 2. Verificamos si hay suficientes palabras para formar un contexto
            if len(tokens) >= n - 1:
                # 3. Extraemos el contexto (las últimas n-1 palabras)
                contexto_actual = tuple(tokens[-(n - 1):])
                
                # 4. Llamamos a nuestro "cerebro" para que busque sugerencias
                #    Asumimos que usaremos el corpus con id=1. 
                #    En una versión más avanzada, podrías añadir otro <select> para esto.
                sugerencias = obtener_sugerencias(contexto_actual, n=n)

                # 5. Preparamos los resultados para enviarlos al HTML
                if sugerencias:
                    context['sugerencia_principal'] = sugerencias[0]
                    context['top_sugerencias'] = sugerencias
                else:
                    context['error'] = f"No se encontraron sugerencias para el contexto: '{' '.join(contexto_actual)}'."
            else:
                context['error'] = f"Necesitas escribir al menos {n - 1} palabra(s) para usar el modelo de {n}-gramas."
    
    # 6. Mostramos la página HTML, pasándole los resultados (o un diccionario vacío la primera vez)
    return render(request, 'analisis/autocomplementar.html', context)