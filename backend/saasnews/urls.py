from django.contrib import admin
from django.urls import path, include
from noticias.views import home  # Supondo que você tenha uma view 'home' definida

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('noticias.urls')),  # Inclui URLs do app noticias
    path('', home, name='home'),  # Rota raiz para a home
]
