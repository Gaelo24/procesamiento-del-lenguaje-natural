"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from analisis.views import home  
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
        <h1>Bienvenido al Sistema de Procesamiento de Lenguaje Natural</h1>
        <p><a href='/subir/'>Subir texto</a></p>
        <p><a href='/lista/'>Ver textos analizados</a></p>
        <p><a href='/admin/'>Administración</a></p>
    """)


urlpatterns = [
    path("", home, name="home"),
    path('admin/', admin.site.urls),
   # path("subir/", subir_texto, name="cargar_texto"),
   # path("lista/", listar_textos, name="listar_textos"),
    path('', include('analisis.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)