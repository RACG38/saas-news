from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('noticias.urls')),  # Inclui URLs do app noticias
    
]
