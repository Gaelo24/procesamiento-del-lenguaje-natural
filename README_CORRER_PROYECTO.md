# Cómo ejecutar el proyecto (PLN avance 2)

## Requisitos
- Python 3.10+
- (Opcional) pipenv

## Pasos
```bash
cd "/mnt/data/PLN_avance2_extracted/Procesamiento de lenguaje natural"
# Entorno
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # instala Django

# Migraciones y arranque
python manage.py migrate
python manage.py runserver
```

Luego abre http://127.0.0.1:8000/

## Limpieza integrada (minúsculas, sin puntuación, sin stopwords)
El flujo de carga ahora procesa el archivo de texto y:
- Convierte a minúsculas.
- Elimina signos de puntuación (se extraen solo tokens alfabéticos).
- Elimina stopwords en español (lista incorporada).
- Calcula frecuencias y llena el modelo `Palabra`.

### Dónde está la lógica
- `analisis/preprocesamiento.py`: STOPWORDS + funciones `clean_and_filter` y `frequencies`.
- `analisis/views.py`: en `subir_texto`, después de `form.save()` se lee el archivo, se limpia, se tokeniza y se guardan frecuencias.

## Verificación
1) Sube un `.txt` en `/subir/`.
2) Vuelve a la página principal y confirma que aparecen tokens y frecuencias bajo el título.
3) De ser necesario, borra `db.sqlite3` para reiniciar datos y repite pruebas.

## Commit sugerido
Si tu proyecto está versionado con Git, ejecuta desde la raíz del proyecto:
```bash
git add analisis/preprocesamiento.py analisis/views.py README_CORRER_PROYECTO.md
git commit -m "Limpieza de texto: minúsculas, eliminación de puntuación y stopwords en español; integración en flujo de carga y guardado de frecuencias"
```

## Tokens y Nube de Palabras
- Se guardan **tokens procesados** (sin puntuación y sin stopwords) en `TextoAnalizado.tokens_json`.
- Se genera una **nube de palabras** por texto y se guarda como imagen en `TextoAnalizado.nube_imagen` (carpeta `media/wordclouds/`).

### Requisitos nuevos
Instala dependencias adicionales:
```bash
pip install -r requirements.txt
```

### Migraciones
Como se agregaron campos al modelo, ejecuta:
```bash
python manage.py makemigrations analisis
python manage.py migrate
```

### Commit sugerido
```bash
git add analisis/models.py analisis/views.py analisis/templates/analisis/lista.html requirements.txt README_CORRER_PROYECTO.md
git commit -m "Tokens procesados y nube de palabras: JSONField e ImageField en TextoAnalizado; generación tras la carga del archivo; plantilla actualizada"
```
