# en analisis/forms.py
from django import forms
from .models import TextoAnalizado

class TextoAnalizadoForm(forms.ModelForm):
    class Meta:
        model = TextoAnalizado
        fields = ['archivo'] 