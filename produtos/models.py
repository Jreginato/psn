from django.db import models
from django.conf import settings
from django.utils.text import slugify
from decimal import Decimal


class Categoria(models.Model):
    """Categorias de produtos: Ebooks, Cursos, Treinos, etc"""
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField(blank=True)
    icone = models.CharField(max_length=50, blank=True, help_text="Classe do ícone (ex: fa-book, fa-video)")
    ordem = models.PositiveIntegerField(default=0, help_text="Ordem de exibição")
    ativo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['ordem', 'nome']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nome


class Produto(models.Model):
    """Produtos digitais - Separação entre página comercial e conteúdo"""
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('publicado', 'Publicado'),
        ('arquivado', 'Arquivado'),
    ]
    
    # === INFORMAÇÕES BÁSICAS ===
    nome = models.CharField('Nome do Produto', max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='produtos')
    
    # === PÁGINA DE VENDAS (Parte Comercial) ===
    # Hero Section
    titulo_hero = models.CharField('Título Principal', max_length=150, blank=True, default='', help_text="Ex: Treino para Hipertrofia Muscular")
    subtitulo_hero = models.CharField('Subtítulo', max_length=250, blank=True, default='', help_text="Ex: Protocolo completo para ganhar massa muscular de forma eficiente")
    
    # Descrição Comercial
    texto_introducao = models.TextField('Texto de Introdução', blank=True, default='', help_text="Parágrafo inicial vendendo o produto")
    
    # O que está incluso (bullets)
    item_incluso_1 = models.CharField('Item Incluso 1', max_length=200, blank=True, default='')
    item_incluso_2 = models.CharField('Item Incluso 2', max_length=200, blank=True, default='')
    item_incluso_3 = models.CharField('Item Incluso 3', max_length=200, blank=True, default='')
    item_incluso_4 = models.CharField('Item Incluso 4', max_length=200, blank=True, default='')
    item_incluso_5 = models.CharField('Item Incluso 5', max_length=200, blank=True, default='')
    
    # Para quem é este produto
    para_quem_titulo = models.CharField('Título "Para Quem"', max_length=100, blank=True, default='')
    para_quem_texto = models.TextField('Texto "Para Quem"', blank=True, default='', help_text="Descreva o público-alvo")
    
    # Benefícios/Resultados
    beneficio_1_titulo = models.CharField('Benefício 1 - Título', max_length=100, blank=True, default='')
    beneficio_1_descricao = models.TextField('Benefício 1 - Descrição', blank=True, default='')
    
    beneficio_2_titulo = models.CharField('Benefício 2 - Título', max_length=100, blank=True, default='')
    beneficio_2_descricao = models.TextField('Benefício 2 - Descrição', blank=True, default='')
    
    beneficio_3_titulo = models.CharField('Benefício 3 - Título', max_length=100, blank=True, default='')
    beneficio_3_descricao = models.TextField('Benefício 3 - Descrição', blank=True, default='')
    
    # Garantia/CTA
    texto_garantia = models.TextField('Texto de Garantia', blank=True, default='', help_text="Ex: 7 dias de garantia incondicional")
    texto_cta = models.CharField('Texto do Botão', max_length=50, default="Comprar Agora")
    
    # === MÍDIAS COMERCIAIS ===
    imagem_capa = models.ImageField('Imagem de Capa', upload_to='produtos/capas/', blank=True, help_text="Imagem principal do produto")
    imagem_destaque = models.ImageField('Imagem Destaque', upload_to='produtos/destaques/', blank=True, help_text="Imagem para banners/destaques")
    video_vendas = models.URLField('Vídeo de Vendas', blank=True, help_text="URL do vídeo de vendas (YouTube, Vimeo)")
    
    # === PREÇO ===
    preco = models.DecimalField('Preço', max_digits=10, decimal_places=2)
    preco_promocional = models.DecimalField('Preço Promocional', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # === CONTROLE ===
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='rascunho')
    destaque = models.BooleanField('Produto em Destaque', default=False, help_text="Exibir na home e topo do catálogo")
    ordem = models.PositiveIntegerField('Ordem de Exibição', default=0, help_text="Ordem no catálogo (menor = primeiro)")
    
    # === METADADOS ===
    total_vendas = models.PositiveIntegerField(default=0, editable=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['-destaque', 'ordem', '-criado_em']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.nome
    
    @property
    def preco_final(self):
        """Retorna preço promocional se existir, senão preço normal"""
        return self.preco_promocional if self.preco_promocional else self.preco
    
    @property
    def tem_promocao(self):
        return self.preco_promocional is not None and self.preco_promocional < self.preco
    
    @property
    def desconto_percentual(self):
        """Calcula percentual de desconto"""
        if self.tem_promocao:
            return int(((self.preco - self.preco_promocional) / self.preco) * 100)
        return 0
    
    def get_itens_inclusos(self):
        """Retorna lista de itens inclusos não vazios"""
        itens = []
        for i in range(1, 6):
            item = getattr(self, f'item_incluso_{i}', '')
            if item:
                itens.append(item)
        return itens
    
    def get_beneficios(self):
        """Retorna lista de benefícios não vazios"""
        beneficios = []
        for i in range(1, 4):
            titulo = getattr(self, f'beneficio_{i}_titulo', '')
            descricao = getattr(self, f'beneficio_{i}_descricao', '')
            if titulo and descricao:
                beneficios.append({'titulo': titulo, 'descricao': descricao})
        return beneficios


class ConteudoDigital(models.Model):
    """Conteúdos que compõem um produto (PDFs, vídeos, aulas, etc)"""
    TIPO_CHOICES = [
        ('pdf', 'PDF'),
        ('video', 'Vídeo'),
        ('video_url', 'Vídeo (URL)'),
        ('imagem', 'Imagem/Planilha'),
        ('texto', 'Texto/HTML'),
        ('zip', 'Arquivo ZIP'),
        ('link', 'Link Externo'),
    ]
    
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='conteudos')
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    ordem = models.PositiveIntegerField(default=0)
    
    # Diferentes tipos de conteúdo
    arquivo = models.FileField(upload_to='produtos/conteudos/', blank=True, null=True, help_text="Para PDF, vídeo, ZIP")
    imagem = models.ImageField(upload_to='produtos/imagens/', blank=True, null=True, help_text="Para planilhas de treino, infográficos, etc")
    url_externa = models.URLField(blank=True, help_text="Para vídeos externos ou links")
    texto_html = models.TextField(blank=True, help_text="Para conteúdo em texto/HTML")
    
    # Metadados
    descricao = models.TextField(blank=True)
    duracao = models.CharField(max_length=50, blank=True, help_text="Ex: 45min, 120 páginas")
    liberado = models.BooleanField(default=True, help_text="Conteúdo disponível para acesso")
    
    class Meta:
        verbose_name = "Conteúdo Digital"
        verbose_name_plural = "Conteúdos Digitais"
        ordering = ['ordem', 'titulo']
    
    def __str__(self):
        return f"{self.produto.nome} - {self.titulo}"


class Pedido(models.Model):
    """Pedidos/Compras realizadas"""
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('aprovado', 'Aprovado'),
        ('cancelado', 'Cancelado'),
        ('reembolsado', 'Reembolsado'),
    ]
    
    # Cliente
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='pedidos')
    
    # Valores
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status e pagamento
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    metodo_pagamento = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=200, blank=True, help_text="ID da transação no gateway")
    
    # Dados do cliente no momento da compra
    email_compra = models.EmailField()
    nome_compra = models.CharField(max_length=200)
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    aprovado_em = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.email}"
    
    def liberar_acesso_produtos(self):
        """Libera acesso aos produtos quando o pedido é aprovado"""
        for item in self.itens.all():
            AcessoProduto.objects.get_or_create(
                usuario=self.usuario,
                produto=item.produto
            )


class ItemPedido(models.Model):
    """Itens individuais de um pedido"""
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    
    # Valores no momento da compra
    nome_produto = models.CharField(max_length=200)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens dos Pedidos"
    
    def __str__(self):
        return f"{self.nome_produto} - Pedido #{self.pedido.id}"


class AcessoProduto(models.Model):
    """Controla quais produtos cada usuário tem acesso"""
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='acessos')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='acessos')
    
    # Controle de acesso
    liberado_em = models.DateTimeField(auto_now_add=True)
    expira_em = models.DateTimeField(null=True, blank=True, help_text="Deixe vazio para acesso vitalício")
    ativo = models.BooleanField(default=True)
    
    # Rastreamento
    ultimo_acesso = models.DateTimeField(null=True, blank=True)
    total_acessos = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = "Acesso ao Produto"
        verbose_name_plural = "Acessos aos Produtos"
        unique_together = ['usuario', 'produto']
        ordering = ['-liberado_em']
    
    def __str__(self):
        return f"{self.usuario.email} - {self.produto.nome}"
    
    @property
    def is_ativo(self):
        """Verifica se o acesso está ativo e não expirado"""
        if not self.ativo:
            return False
        if self.expira_em:
            from django.utils import timezone
            return timezone.now() < self.expira_em
        return True
