from django.contrib import admin
from .models import Cliente, Plano, AcaoSelecionada


admin.site.register(Cliente)
admin.site.register(Plano)
admin.site.register(AcaoSelecionada)