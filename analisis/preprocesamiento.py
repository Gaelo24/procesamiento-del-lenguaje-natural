# analisis/preprocesamiento.py

import re
from collections import defaultdict
from typing import List, Tuple

# --- SECCIÓN 1: HERRAMIENTAS PARA ANÁLISIS DE LENGUAJE NATURAL ---

STOP_WORDS = tuple([
    "a", "ademas", "al", "algo", "algunas", "algunos", "ante", "antes", "aunque", "aún",
    "bajo", "cabe", "cada", "cierto", "como", "con", "contra", "cual", "cuales",
    "cuando", "cuanta", "cuantas", "cuanto", "cuantos", "cuál", "cuáles", "cuán", "cómo",
    "de", "del", "desde", "donde", "dos", "dónde", "el", "ella", "ellas", "ellos", "en",
    "entre", "era", "erais", "eramos", "eran", "eres", "es", "esa", "esas", "ese", "esos",
    "esta", "estaban", "estamos", "estan", "estas", "este", "esto", "estos", "estoy",
    "está", "estábamos", "están", "estás", "fue", "fueron", "fui", "fuimos", "fuiste",
    "ha", "habido", "había", "habíamos", "habían", "hace", "haceis", "hacemos", "hacen",
    "hacer", "hacia", "haciendo", "han", "hasta", "hay", "hicieron", "hizo", "incluso",
    "jamás", "junto", "la", "las", "le", "les", "lo", "los", "mas", "me", "mi", "mis",
    "mucha", "muchas", "mucho", "muchos", "muy", "nada", "ni", "ninguna", "ningunas",
    "ninguno", "ningunos", "no", "nos", "nosotras", "nosotros", "nunca", "o", "os",
    "otra", "otras", "otro", "otros", "para", "pero", "poca", "pocas", "poco", "pocos",
    "por", "porque", "posiblemente", "primer", "primera", "primeras", "primeros",
    "propia", "propias", "propio", "propios", "que", "quien", "quienes", "qué", "se",
    "según", "ser", "si", "siendo", "sin", "sino", "sobre", "solamente", "solo", "somos",
    "soy", "sr", "sra", "sres", "su", "sus", "suya", "suyas", "suyo", "suyos", "sí",
    "sólo", "tal", "tales", "también", "tampoco", "tan", "tanto", "te", "tendremos",
    "tendrá", "tendrán", "teneis", "tenemos", "tengo", "tiene", "tienen", "tienes",
    "toda", "todas", "todo", "todos", "tras", "tu", "tus", "tuya", "tuyas", "tuyo",
    "tuyos", "un", "una", "unas", "uno", "unos", "usted", "ustedes", "vais", "vamos",
    "van", "vosotros", "voy", "vuestra", "vuestras", "vuestro", "vuestros", "y", "ya",
    "yo", "él", "ése", "ésa", "ésos", "ésas"
])

def tokenizar(texto: str) -> List[str]:
    """Divide un texto en palabras (letras y acentos incluidos)."""
    texto = texto.lower()
    return re.findall(r"[a-záéíóúñü]+", texto)

def limpiar_tokens(texto: str) -> List[str]:
    """Tokeniza y elimina stopwords, devolviendo solo palabras relevantes."""
    palabras = tokenizar(texto)
    return [p for p in palabras if p not in STOP_WORDS]

def contar_palabras(lista_palabras: list) -> dict:
    """Cuenta frecuencia de cada token."""
    conteo = defaultdict(int)
    for palabra in lista_palabras:
        conteo[palabra] += 1
    return dict(conteo)

# --- Alias para compatibilidad ---
def clean_and_filter(texto: str) -> List[str]:
    return limpiar_tokens(texto)

def frequencies(tokens: list) -> dict:
    return contar_palabras(tokens)

# --- Funciones para N-Gramas ---
def generar_ngramas(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
    if n <= 0: return []
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return list(ngrams)

def generar_unigramas(tokens: List[str]) -> List[Tuple[str, ...]]:
    return generar_ngramas(tokens, 1)

def generar_bigramas(tokens: List[str]) -> List[Tuple[str, ...]]:
    return generar_ngramas(tokens, 2)

def generar_trigramas(tokens: List[str]) -> List[Tuple[str, ...]]:
    return generar_ngramas(tokens, 3)

# --- SECCIÓN 2: LÓGICA PARA EL RECONOCEDOR LÉXICO (EXAMEN) ---

# --- Árbol Binario de Búsqueda ---
class Nodo:
    def __init__(self, valor):
        self.valor = valor
        self.izquierda = None
        self.derecha = None

class ArbolBinarioBusqueda:
    def __init__(self):
        self.raiz = None
    def insertar(self, valor):
        if self.raiz is None: self.raiz = Nodo(valor)
        else: self._insertar_recursivo(self.raiz, valor)
    def _insertar_recursivo(self, nodo_actual, valor):
        if valor < nodo_actual.valor:
            if nodo_actual.izquierda is None: nodo_actual.izquierda = Nodo(valor)
            else: self._insertar_recursivo(nodo_actual.izquierda, valor)
        elif valor > nodo_actual.valor:
            if nodo_actual.derecha is None: nodo_actual.derecha = Nodo(valor)
            else: self._insertar_recursivo(nodo_actual.derecha, valor)
    def buscar(self, valor):
        return self._buscar_recursivo(self.raiz, valor)
    def _buscar_recursivo(self, nodo_actual, valor):
        if nodo_actual is None or nodo_actual.valor == valor: return nodo_actual is not None
        if valor < nodo_actual.valor: return self._buscar_recursivo(nodo_actual.izquierda, valor)
        else: return self._buscar_recursivo(nodo_actual.derecha, valor)

# --- Analizador Léxico ---
class AnalizadorLexico:
    def __init__(self, codigo_fuente, abb_reservadas):
        self.codigo = codigo_fuente
        self.posicion = 0
        self.tokens = []
        self.abb_reservadas = abb_reservadas

    def analizar(self):
        while self.posicion < len(self.codigo):
            char_actual = self.codigo[self.posicion]

            if char_actual.isspace():
                self.posicion += 1
                continue
            
            if char_actual.isalpha() or char_actual == '_':
                self.manejar_identificador()
            elif char_actual.isdigit():
                self.manejar_numero()
            elif char_actual == '/':
                self.manejar_diagonal()
            elif char_actual in "()[]{}<>;=+-*":
                self.agregar_token("SIMBOLO", char_actual)
            else:
                self.agregar_token("DESCONOCIDO", char_actual)
        
        return self.tokens

    def agregar_token(self, tipo, valor):
        self.tokens.append((tipo, valor))
        self.posicion += len(valor)

    def manejar_identificador(self):
        inicio = self.posicion
        while self.posicion < len(self.codigo) and \
              (self.codigo[self.posicion].isalnum() or self.codigo[self.posicion] == '_'):
            self.posicion += 1
        
        lexema = self.codigo[inicio:self.posicion]

        if self.abb_reservadas.buscar(lexema):
            self.tokens.append(("PALABRA_RESERVADA", lexema))
        else:
            self.tokens.append(("ID", lexema))

    def manejar_numero(self):
        inicio = self.posicion
        while self.posicion < len(self.codigo) and self.codigo[self.posicion].isdigit():
            self.posicion += 1
        lexema = self.codigo[inicio:self.posicion]
        self.tokens.append(("NUMERO", lexema))
    
    def manejar_diagonal(self):
        if self.posicion + 1 < len(self.codigo) and self.codigo[self.posicion + 1] == '*':
            inicio = self.posicion
            try:
                fin = self.codigo.index('*/', self.posicion + 2) + 2
                lexema = self.codigo[inicio:fin]
                self.tokens.append(("COMENTARIO_LARGO", lexema))
                self.posicion = fin
            except ValueError:
                error_msg = f"Comentario largo iniciado en la posición {inicio} no fue cerrado."
                self.tokens.append(("ERROR_LEXICO", error_msg))
                self.posicion = len(self.codigo)
        else:
            self.agregar_token("OParitmetico", "/")



# --- SECCIÓN 3: LÓGICA PARA EL TINY PARSER ---

# --- Analizador Léxico del Tiny ---

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

# ---Analizador Sintáctico Descendente ---

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