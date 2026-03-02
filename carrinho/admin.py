from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.utils import timezone
from .models import Cupom


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):
    list_display = [
        'codigo', 'tipo', 'valor_formatado', 'valor_minimo_pedido',
        'status_badge', 'validade', 'uso_maximo', 'total_usado', 'criado_em'
    ]
    list_filter = ['ativo', 'tipo']
    search_fields = ['codigo']
    readonly_fields = ['total_usado', 'criado_em']
    ordering = ['-criado_em']

    fieldsets = [
        ('Cupôm', {
            'fields': ('codigo', 'ativo')
        }),
        ('Desconto', {
            'fields': ('tipo', 'valor', 'valor_minimo_pedido')
        }),
        ('Limites de Uso', {
            'fields': ('validade', 'uso_maximo', 'total_usado')
        }),
        ('Auditoria', {
            'fields': ('criado_em',),
            'classes': ('collapse',)
        }),
    ]

    def valor_formatado(self, obj):
        if obj.tipo == 'percentual':
            return f'{obj.valor}%'
        return f'R$ {obj.valor}'
    valor_formatado.short_description = 'Desconto'

    def status_badge(self, obj):
        if not obj.ativo:
            return mark_safe('<span style="color:#dc2626;font-weight:600;">&#x25CF; Inativo</span>')
        if obj.validade and timezone.now() > obj.validade:
            return mark_safe('<span style="color:#d97706;font-weight:600;">&#x25CF; Expirado</span>')
        if obj.uso_maximo is not None and obj.total_usado >= obj.uso_maximo:
            return mark_safe('<span style="color:#d97706;font-weight:600;">&#x25CF; Esgotado</span>')
        return mark_safe('<span style="color:#16a34a;font-weight:600;">&#x25CF; Ativo</span>')
    status_badge.short_description = 'Status'
