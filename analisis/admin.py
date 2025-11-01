from django.contrib import admin
from .models import TextoAnalizado, Palabra, Bigrama, Trigrama

admin.site.register(TextoAnalizado)
admin.site.register(Palabra)
admin.site.register(Bigrama)   
admin.site.register(Trigrama)
