from django.urls import path
from . import views 

urlpatterns = [ 
    path('subir/', views.cargar_texto, name='cargar_texto'),
    path('lista/', views.listar_textos, name='listar_textos'),
    path('sugerir/', views.autocompletar_view, name='autocompletar'),
    path('reconocedor/', views.reconocedor_view, name='reconocedor'),
    path('tiny-parser/', views.tiny_parser_view, name='tiny_parser'),
]
