from django.contrib import admin
from .models import Cliente, Plano, AcaoSelecionada, Noticia, Token, Endereco


admin.site.register(Cliente)
admin.site.register(Plano)
admin.site.register(AcaoSelecionada)
admin.site.register(Noticia)
admin.site.register(Token)
admin.site.register(Endereco)


