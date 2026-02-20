from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import Categoria, Produto, ConteudoDigital, Pedido, ItemPedido, AcessoProduto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'ordem', 'total_produtos', 'ativo']
    list_editable = ['ordem', 'ativo']
    search_fields = ['nome', 'descricao']
    prepopulated_fields = {'slug': ('nome',)}
    
    def total_produtos(self, obj):
        return obj.produtos.count()
    total_produtos.short_description = 'Produtos'


class ConteudoDigitalInline(admin.TabularInline):
    model = ConteudoDigital
    extra = 1
    fields = ['titulo', 'tipo', 'ordem', 'liberado']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'preco_display', 'status', 'destaque', 'total_vendas', 'criado_em']
    list_filter = ['status', 'categoria', 'destaque', 'criado_em']
    list_editable = ['destaque', 'status']
    search_fields = ['nome', 'titulo_hero', 'subtitulo_hero']
    prepopulated_fields = {'slug': ('nome',)}
    readonly_fields = ['total_vendas', 'criado_em', 'atualizado_em', 'preview_capa', 'preview_destaque']
    inlines = [ConteudoDigitalInline]
    
    fieldsets = (
        ('📌 Informações Básicas', {
            'fields': ('nome', 'slug', 'categoria', 'status', 'destaque', 'ordem')
        }),
        ('🎯 Página de Vendas - Hero', {
            'fields': ('titulo_hero', 'subtitulo_hero', 'texto_introducao'),
            'description': 'Conteúdo principal da página de vendas'
        }),
        ('✅ O que está Incluso', {
            'fields': ('item_incluso_1', 'item_incluso_2', 'item_incluso_3', 'item_incluso_4', 'item_incluso_5'),
            'classes': ('collapse',)
        }),
        ('👤 Para Quem é Este Produto', {
            'fields': ('para_quem_titulo', 'para_quem_texto'),
            'classes': ('collapse',)
        }),
        ('💎 Benefícios/Resultados', {
            'fields': (
                'beneficio_1_titulo', 'beneficio_1_descricao',
                'beneficio_2_titulo', 'beneficio_2_descricao',
                'beneficio_3_titulo', 'beneficio_3_descricao'
            ),
            'classes': ('collapse',)
        }),
        ('🔒 Garantia e CTA', {
            'fields': ('texto_garantia', 'texto_cta'),
            'classes': ('collapse',)
        }),
        ('🖼️ Mídias', {
            'fields': ('imagem_capa', 'preview_capa', 'imagem_destaque', 'preview_destaque', 'video_vendas')
        }),
        ('💰 Preço', {
            'fields': ('preco', 'preco_promocional')
        }),
        ('📊 Estatísticas', {
            'fields': ('total_vendas', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def preco_display(self, obj):
        if obj.tem_promocao:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">R$ {}</span> '
                '<span style="color: #0f9d58; font-weight: bold;">R$ {}</span> '
                '<span style="background: #0f9d58; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">-{}%</span>',
                obj.preco, obj.preco_promocional, obj.desconto_percentual
            )
        return f'R$ {obj.preco}'
    preco_display.short_description = 'Preço'
    
    def preview_capa(self, obj):
        if obj.imagem_capa:
            return format_html('<img src="{}" style="max-height: 200px; border-radius: 8px;" />', obj.imagem_capa.url)
        return "Sem imagem"
    preview_capa.short_description = 'Preview Capa'
    
    def preview_destaque(self, obj):
        if obj.imagem_destaque:
            return format_html('<img src="{}" style="max-height: 200px; border-radius: 8px;" />', obj.imagem_destaque.url)
        return "Sem imagem"
    preview_destaque.short_description = 'Preview Destaque'


@admin.register(ConteudoDigital)
class ConteudoDigitalAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'produto', 'tipo', 'ordem', 'liberado']
    list_filter = ['tipo', 'liberado', 'produto__categoria']
    list_editable = ['ordem', 'liberado']
    search_fields = ['titulo', 'produto__nome']


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['produto', 'nome_produto', 'preco_unitario', 'quantidade', 'subtotal']
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'total', 'status', 'metodo_pagamento', 'criado_em']
    list_filter = ['status', 'metodo_pagamento', 'criado_em']
    search_fields = ['usuario__email', 'usuario__first_name', 'transaction_id']
    readonly_fields = ['subtotal', 'desconto', 'total', 'criado_em', 'atualizado_em', 'aprovado_em']
    inlines = [ItemPedidoInline]
    
    fieldsets = (
        ('Cliente', {
            'fields': ('usuario', 'nome_compra', 'email_compra')
        }),
        ('Valores', {
            'fields': ('subtotal', 'desconto', 'total')
        }),
        ('Pagamento', {
            'fields': ('status', 'metodo_pagamento', 'transaction_id')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em', 'aprovado_em')
        }),
    )
    
    actions = ['aprovar_pedidos', 'cancelar_pedidos']
    
    def aprovar_pedidos(self, request, queryset):
        from django.utils import timezone
        for pedido in queryset:
            pedido.status = 'aprovado'
            pedido.aprovado_em = timezone.now()
            pedido.save()
            pedido.liberar_acesso_produtos()
        self.message_user(request, f'{queryset.count()} pedido(s) aprovado(s) e acessos liberados.')
    aprovar_pedidos.short_description = 'Aprovar pedidos selecionados'
    
    def cancelar_pedidos(self, request, queryset):
        queryset.update(status='cancelado')
        self.message_user(request, f'{queryset.count()} pedido(s) cancelado(s).')
    cancelar_pedidos.short_description = 'Cancelar pedidos selecionados'


@admin.register(AcessoProduto)
class AcessoProdutoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'produto', 'liberado_em', 'expira_em', 'ativo', 'is_ativo_display']
    list_filter = ['ativo', 'liberado_em', 'produto__categoria']
    search_fields = ['usuario__email', 'produto__nome']
    readonly_fields = ['liberado_em', 'total_acessos', 'ultimo_acesso']
    
    def is_ativo_display(self, obj):
        if obj.is_ativo:
            return mark_safe('<span style="color: #0f9d58;">✓ Ativo</span>')
        return mark_safe('<span style="color: #d93025;">✗ Inativo</span>')
    is_ativo_display.short_description = 'Status'
