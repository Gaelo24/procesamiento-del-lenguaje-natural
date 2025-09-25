from django.urls import path
from . import views 

urlpatterns = [ 
    path('subir/', views.cargar_texto, name='cargar_texto'),
    path('lista/', views.listar_textos, name='listar_textos'),
    path('sugerir/', views.autocomplementar_view, name='autocomplementar'), 
]
