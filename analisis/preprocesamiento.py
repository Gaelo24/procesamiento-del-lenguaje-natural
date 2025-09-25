import re
from collections import defaultdict
from typing import List, Tuple

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

def tokenizar(texto: str) -> list:
    """Divide un texto en palabras (letras y acentos incluidos)."""
    texto = texto.lower()
    return re.findall(r"[a-záéíóúñü]+", texto)

def limpiar_tokens(texto: str) -> list:
    """Elimina stopwords y devuelve solo palabras relevantes."""
    palabras = dividir_texto(texto)
    return [p for p in palabras if p not in STOP_WORDS]

def contar_palabras(lista_palabras: list) -> dict:
    """Cuenta frecuencia de cada token."""
    conteo = defaultdict(int)
    for palabra in lista_palabras:
        conteo[palabra] += 1
    return dict(conteo)

def clean_and_filter(texto: str) -> list:
    """Alias para limpiar_tokens."""
    return limpiar_tokens(texto)

def frequencies(tokens: list) -> dict:
    """Alias para contar_palabras."""
    return contar_palabras(tokens)

def generar_ngramas(tokens: List[str], n: int) -> List[Tuple[str, ...]]:
    """
    Función genérica para crear n-gramas a partir de una lista de tokens.
    
    Args:
        tokens: La lista de palabras ya tokenizada.
        n: El tamaño del n-grama (1 para unigramas, 2 para bigramas, etc.).

    Returns:
        Una lista de tuplas, donde cada tupla es un n-grama.
    """
    if n <= 0:
        return []
    ngrams = zip(*[tokens[i:] for i in range(n)])
    return list(ngrams)

def generar_unigramas(tokens: List[str]) -> List[Tuple[str, ...]]:
    """Genera unigramas (1-gramas)."""
    return generar_ngramas(tokens, 1)

def generar_bigramas(tokens: List[str]) -> List[Tuple[str, ...]]:
    """Genera bigramas (2-gramas)."""
    return generar_ngramas(tokens, 2)

def generar_trigramas(tokens: List[str]) -> List[Tuple[str, ...]]:
    """Genera trigramas (3-gramas)."""
    return generar_ngramas(tokens, 3)
