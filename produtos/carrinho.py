"""
Sistema de Carrinho de Compras usando Session
"""
from decimal import Decimal
from django.conf import settings
from .models import Produto


class Carrinho:
    """Gerenciador de carrinho de compras na sessão"""
    
    def __init__(self, request):
        self.session = request.session
        carrinho = self.session.get(settings.CART_SESSION_ID)
        if not carrinho:
            carrinho = self.session[settings.CART_SESSION_ID] = {}
        self.carrinho = carrinho
    
    def adicionar(self, produto):
        """Adiciona um produto ao carrinho"""
        produto_id = str(produto.id)
        if produto_id not in self.carrinho:
            self.carrinho[produto_id] = {
                'produto_id': produto.id,
                'nome': produto.nome,
                'preco': str(produto.preco_final),
                'slug': produto.slug,
            }
        self.salvar()
    
    def remover(self, produto):
        """Remove um produto do carrinho"""
        produto_id = str(produto.id)
        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.salvar()
    
    def salvar(self):
        """Salva o carrinho na sessão"""
        self.session.modified = True
    
    def limpar(self):
        """Limpa o carrinho"""
        del self.session[settings.CART_SESSION_ID]
        self.salvar()
    
    def __iter__(self):
        """Itera sobre os itens do carrinho e busca os produtos"""
        produto_ids = self.carrinho.keys()
        produtos = Produto.objects.filter(id__in=produto_ids)
        carrinho = self.carrinho.copy()
        
        for produto in produtos:
            carrinho[str(produto.id)]['produto'] = produto
        
        for item in carrinho.values():
            item['preco'] = Decimal(item['preco'])
            item['total'] = item['preco']
            yield item
    
    def __len__(self):
        """Retorna a quantidade de itens no carrinho"""
        return len(self.carrinho)
    
    def get_total(self):
        """Retorna o valor total do carrinho"""
        return sum(Decimal(item['preco']) for item in self.carrinho.values())
    
    def get_produtos_ids(self):
        """Retorna lista de IDs dos produtos no carrinho"""
        return [int(id) for id in self.carrinho.keys()]
