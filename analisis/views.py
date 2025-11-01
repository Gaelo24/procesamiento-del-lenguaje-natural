from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from pathlib import Path
from io import BytesIO
from wordcloud import WordCloud
from django.http import HttpResponse

from .preprocesamiento import Lexer, Parser

from .forms import TextoAnalizadoForm
from .models import TextoAnalizado, Palabra, Bigrama, Trigrama
from .preprocesamiento import generar_bigramas, generar_trigramas, contar_palabras, limpiar_tokens, tokenizar
from .sugeridor import obtener_sugerencias
from .preprocesamiento import ArbolBinarioBusqueda, AnalizadorLexico



def cargar_texto(request):
    """
    Vista final para subir un archivo, analizarlo (unigramas, bigramas, trigramas)
    y guardar todos los resultados en la base de datos.
    """
    if request.method == "POST":
        formulario = TextoAnalizadoForm(request.POST, request.FILES)
        if formulario.is_valid():
            # 1. Guarda el formulario en memoria, sin enviarlo a la BD todavía.
            texto_obj = formulario.save(commit=False)
            
            # 2. Obtenemos el nombre del archivo subido.
            nombre_del_archivo = texto_obj.archivo.name
            
            # 3. Asignamos ese nombre al campo 'titulo' del objeto.
            texto_obj.titulo = nombre_del_archivo
            
            # 4. Ahora sí, guardamos el objeto completo en la base de datos.
            texto_obj.save()

            # El bloque 'try' debe estar correctamente indentado aquí
            try:
                contenido = Path(texto_obj.archivo.path).read_text(encoding="utf-8", errors="ignore")
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

def autocompletar_view(request):
    context = {}
    
    # Si el usuario envió el formulario (hizo clic en el botón "Sugerir")
    if request.method == 'POST':
        texto_usuario = request.POST.get('texto_usuario', '')
        n = int(request.POST.get('n_grama', 2))
        
        # Guardamos los datos actuales para mostrarlos de nuevo en el formulario
        context['texto_actual'] = texto_usuario
        context['n_actual'] = n

        if texto_usuario:
            # 1. Convertimos el texto del usuario en una lista de palabras (tokens)
            tokens = tokenizar(texto_usuario) 
            
            # 2. Verificamos si hay suficientes palabras para formar un contexto
            if len(tokens) >= n - 1:
                # 3. Extraemos el contexto (las últimas n-1 palabras)
                contexto_actual = tuple(tokens[-(n - 1):])
                
                # 4. Llamamos a nuestro "motor" para que busque sugerencias
                sugerencias = obtener_sugerencias(contexto_actual, n=n)

                # 5. Preparamos los resultados para enviarlos al HTML
                if sugerencias:
                    # Guardamos la sugerencia principal
                    context['sugerencia_principal'] = sugerencias[0]
                    
                    # Creamos una nueva lista con el porcentaje ya calculado
                    sugerencias_procesadas = []
                    for palabra, prob in sugerencias:
                        sugerencias_procesadas.append({
                            'palabra': palabra,
                            'prob': prob,
                            'porcentaje': prob * 100  # Hacemos la multiplicación aquí
                        })
                    
                    # Pasamos la nueva lista procesada al template
                    context['top_sugerencias'] = sugerencias_procesadas
                else:
                    context['error'] = f"No se encontraron sugerencias para el contexto: '{' '.join(contexto_actual)}'."
            else:
                context['error'] = f"Necesitas escribir al menos {n - 1} palabra(s) para usar el modelo de {n}-gramas."
    
    # 6. Mostramos la página HTML, pasándole los resultados (o un diccionario vacío la primera vez)
    return render(request, 'analisis/autocompletar.html', context)
    return render(request, 'analisis/autocomplementar.html', context)

def reconocedor_view(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('archivo_codigo'):
        archivo_subido = request.FILES['archivo_codigo']
        
        codigo_fuente = archivo_subido.read().decode('utf-8')

        palabras_reservadas = ["else", "if", "for", "while", "int", "void", "return"]
        abb = ArbolBinarioBusqueda()
        for palabra in palabras_reservadas:
            abb.insertar(palabra)
        
        analizador = AnalizadorLexico(codigo_fuente, abb)
        lista_tokens = analizador.analizar()
        
        # tokens al template 
        context['tokens'] = lista_tokens
        
    return render(request, 'analisis/reconocedor.html', context)



    # En analisis/preprocesamiento.py ... al final del archivo

# --- SECCIÓN 3: LÓGICA PARA EL TINY PARSER (EXAMEN 2) ---

# --- 1. LEXER (Analizador Léxico del Tiny Parser) ---

class Token:
    """Clase para representar un token (tipo y valor)"""
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
    def __str__(self):
        return f"Token({self.tipo}, {self.valor})"

# Tipos de Token
TT_ID       = 'ID'
TT_NUMERO   = 'NUMERO'
TT_MAS      = 'MAS'       # +
TT_MENOS    = 'MENOS'     # -
TT_MULT     = 'MULT'      # *
TT_DIV      = 'DIV'       # /
TT_ASIGNAR  = 'ASIGNAR'   # :=
TT_MAYOR_QUE = 'MAYOR_QUE' # >
TT_IGUAL    = 'IGUAL'     # =
TT_LPAREN   = 'LPAREN'    # (
TT_RPAREN   = 'RPAREN'    # )
TT_PUNTOCOMA = 'PUNTOCOMA' # ;
TT_EOF      = 'EOF'       # Fin de archivo
TT_PALABRA_CLAVE = 'PALABRA_CLAVE'

PALABRAS_CLAVE = [
    "if", "then", "else", "end"
]

class Lexer:
    def __init__(self, texto):
        self.texto = texto
        self.pos = 0
        self.char_actual = self.texto[self.pos] if self.pos < len(self.texto) else None

    def avanzar(self):
        self.pos += 1
        self.char_actual = self.texto[self.pos] if self.pos < len(self.texto) else None

    def saltar_espacios(self):
        while self.char_actual is not None and self.char_actual.isspace():
            self.avanzar()

    def get_numero(self):
        resultado = ""
        while self.char_actual is not None and self.char_actual.isdigit():
            resultado += self.char_actual
            self.avanzar()
        return Token(TT_NUMERO, int(resultado))

    def get_id_o_palabra_clave(self):
        resultado = ""
        while self.char_actual is not None and self.char_actual.isalpha():
            resultado += self.char_actual
            self.avanzar()
        if resultado in PALABRAS_CLAVE:
            return Token(TT_PALABRA_CLAVE, resultado)
        else:
            return Token(TT_ID, resultado)

    def get_token(self):
        while self.char_actual is not None:
            if self.char_actual.isspace():
                self.saltar_espacios()
                continue
            if self.char_actual.isalpha():
                return self.get_id_o_palabra_clave()
            if self.char_actual.isdigit():
                return self.get_numero()
            if self.char_actual == ':' and self.pos + 1 < len(self.texto) and self.texto[self.pos + 1] == '=':
                self.avanzar()
                self.avanzar()
                return Token(TT_ASIGNAR, ':=')
            if self.char_actual == '+':
                self.avanzar(); return Token(TT_MAS, '+')
            if self.char_actual == '-':
                self.avanzar(); return Token(TT_MENOS, '-')
            if self.char_actual == '*':
                self.avanzar(); return Token(TT_MULT, '*')
            if self.char_actual == '/':
                self.avanzar(); return Token(TT_DIV, '/')
            if self.char_actual == '(':
                self.avanzar(); return Token(TT_LPAREN, '(')
            if self.char_actual == ')':
                self.avanzar(); return Token(TT_RPAREN, ')')
            if self.char_actual == '=':
                self.avanzar(); return Token(TT_IGUAL, '=')
            if self.char_actual == '>':
                self.avanzar(); return Token(TT_MAYOR_QUE, '>')
            if self.char_actual == ';':
                self.avanzar(); return Token(TT_PUNTOCOMA, ';')
            if self.char_actual == '$':
                self.avanzar()
                continue
            raise Exception(f"Error Léxico: Carácter '{self.char_actual}' no válido.")
        return Token(TT_EOF, None)

# --- 2. PARSER (Analizador Sintáctico Descendente Recursivo) ---

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token_actual = self.lexer.get_token()

    def error(self, mensaje):
        raise Exception(f"Error Sintáctico: {mensaje}. Se encontró: {self.token_actual}")

    def consumir(self, tipo_token):
        if self.token_actual.tipo == tipo_token:
            self.token_actual = self.lexer.get_token()
        else:
            self.error(f"Se esperaba {tipo_token}")

    def programa(self):
        self.secuencia_sentencias()
        if self.token_actual.tipo != TT_EOF:
            self.error("Se esperaba el fin del archivo, pero hay más tokens.")

    def secuencia_sentencias(self):
        self.sentencia()
        while self.token_actual.tipo == TT_PUNTOCOMA:
            self.consumir(TT_PUNTOCOMA)
            if self.token_actual.tipo == TT_EOF or self.token_actual.valor in ("end", "else"):
                break
            self.sentencia()

    def sentencia(self):
        if self.token_actual.tipo == TT_PALABRA_CLAVE and self.token_actual.valor == 'if':
            self.sent_if()
        elif self.token_actual.tipo == TT_ID:
            self.sent_assign()
        else:
            self.error("Se esperaba un 'if' o un Identificador")

    def sent_if(self):
        self.consumir(TT_PALABRA_CLAVE) # if
        self.expresion()
        self.consumir(TT_PALABRA_CLAVE) # then
        self.secuencia_sentencias()
        if self.token_actual.tipo == TT_PALABRA_CLAVE and self.token_actual.valor == 'else':
            self.consumir(TT_PALABRA_CLAVE) # else
            self.secuencia_sentencias()
        self.consumir(TT_PALABRA_CLAVE) # end

    def sent_assign(self):
        self.consumir(TT_ID)
        self.consumir(TT_ASIGNAR)
        self.expresion()

    def expresion(self):
        self.termino()
        while self.token_actual.tipo in (TT_MAYOR_QUE, TT_IGUAL):
            op = self.token_actual.tipo
            self.consumir(op)
            self.termino()

    def termino(self):
        self.factor()
        while self.token_actual.tipo in (TT_MAS, TT_MENOS):
            op = self.token_actual.tipo
            self.consumir(op)
            self.factor()

    def factor(self):
        self.primario()
        while self.token_actual.tipo in (TT_MULT, TT_DIV):
            op = self.token_actual.tipo
            self.consumir(op)
            self.primario()

    def primario(self):
        if self.token_actual.tipo == TT_LPAREN:
            self.consumir(TT_LPAREN)
            self.expresion()
            self.consumir(TT_RPAREN)
        elif self.token_actual.tipo == TT_ID:
            self.consumir(TT_ID)
        elif self.token_actual.tipo == TT_NUMERO:
            self.consumir(TT_NUMERO)
        else:
            self.error("Se esperaba '(', un Identificador o un Número")

            # Pega esto al final de analisis/views.py

def tiny_parser_view(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('archivo_tiny'):
        archivo_subido = request.FILES['archivo_tiny']
        
        # Leemos el contenido del archivo
        try:
            texto = archivo_subido.read().decode('utf-8')
        except Exception as e:
            context['resultado'] = "RECHAZA"
            context['detalle'] = f"Error al leer el archivo: {e}"
            context['es_error'] = True
            return render(request, 'analisis/tiny_parser.html', context)
        
        # 1. Crear el Lexer
        lexer = Lexer(texto)
        # 2. Crear el Parser
        parser = Parser(lexer)
        
        # 3. Iniciar el análisis
        try:
            parser.programa()
            # Si llega aquí, el programa es válido
            context['resultado'] = "ACEPTA"
            context['detalle'] = f"El archivo '{archivo_subido.name}' es sintácticamente válido."
            context['es_error'] = False
        except Exception as e:
            # Si el Parser lanza una excepción, el programa es inválido
            context['resultado'] = "RECHAZA"
            context['detalle'] = str(e) # Esto mostrará el mensaje de error del parser
            context['es_error'] = True
            
    return render(request, 'analisis/tiny_parser.html', context)