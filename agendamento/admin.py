from django.contrib import admin
from .models import Agendamento

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'data_desejada', 'horario_desejado', 'objetivo', 'status', 'criado_em')
    list_filter = ('status', 'objetivo', 'data_desejada')
    search_fields = ('nome', 'email', 'telefone')
    date_hierarchy = 'data_desejada'
    ordering = ('-criado_em',)
