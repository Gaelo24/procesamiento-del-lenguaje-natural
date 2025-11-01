# probar_analizador.py

# 1. Importamos las clases necesarias de tu módulo de preprocesamiento
from analisis.preprocesamiento import ArbolBinarioBusqueda, AnalizadorLexico

# 2. Definimos un código fuente de ejemplo para analizar
#    Contiene todos los tipos de tokens que tu analizador debe reconocer.
codigo_de_prueba = """
/*
  Este es un comentario largo
  para probar el analizador léxico.
*/
void calcularSuma(int limite) {
    int resultado = 0;
    for (int i = 0; i < limite; i = i + 1) {
        if (i > 5) {
            resultado = resultado * i;
        }
    }
    return resultado;
}
"""

# 3. Definimos las palabras reservadas y creamos el Árbol Binario
palabras_reservadas = ["else", "if", "for", "while", "int", "void", "return"]
abb = ArbolBinarioBusqueda()
for palabra in palabras_reservadas:
    abb.insertar(palabra)

# --- EJECUCIÓN DE LA PRUEBA ---

print("--- Iniciando prueba del Analizador Léxico ---")

# 4. Creamos una instancia de tu analizador
analizador = AnalizadorLexico(codigo_de_prueba, abb)

# 5. Ejecutamos el análisis para obtener la lista de tokens
lista_de_tokens = analizador.analizar()

print("--- Análisis Completado ---")
print("Se reconocieron los siguientes tokens:\n")

# 6. Imprimimos los resultados de forma ordenada
print(f"{'Tipo de Token':<20} | {'Lexema'}")
print("-" * 20 + "-+-" + "-" * 20)

for tipo, lexema in lista_de_tokens:
    # Usamos repr() en el lexema para ver claramente los saltos de línea
    print(f"{tipo:<20} | {repr(lexema)}")
