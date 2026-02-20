from decimal import Decimal
from django.conf import settings
from produtos.models import Produto


class Carrinho:
    """
    Classe para gerenciar o carrinho de compras usando sessão do Django.
    """
    
    def __init__(self, request):
        """
        Inicializa o carrinho com a sessão do request.
        """
        self.session = request.session
        carrinho = self.session.get(settings.CART_SESSION_ID)
        
        if not carrinho:
            # Salva um carrinho vazio na sessão
            carrinho = self.session[settings.CART_SESSION_ID] = {}
        
        self.carrinho = carrinho
    
    def add(self, produto, quantidade=1, substituir_quantidade=False):
        """
        Adiciona um produto ao carrinho ou atualiza sua quantidade.
        
        Args:
            produto: Instância do modelo Produto
            quantidade: Quantidade a adicionar (padrão 1)
            substituir_quantidade: Se True, substitui a quantidade ao invés de somar
        """
        produto_id = str(produto.id)
        
        if produto_id not in self.carrinho:
            self.carrinho[produto_id] = {
                'quantidade': 0,
                'preco': str(produto.preco_final)
            }
        
        if substituir_quantidade:
            self.carrinho[produto_id]['quantidade'] = quantidade
        else:
            self.carrinho[produto_id]['quantidade'] += quantidade
        
        self.save()
    
    def save(self):
        """
        Marca a sessão como modificada para garantir que seja salva.
        """
        self.session.modified = True
    
    def remove(self, produto):
        """
        Remove um produto do carrinho.
        
        Args:
            produto: Instância do modelo Produto ou ID do produto
        """
        produto_id = str(produto.id if hasattr(produto, 'id') else produto)
        
        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.save()
    
    def __iter__(self):
        """
        Itera pelos itens no carrinho e busca os produtos no banco de dados.
        """
        produtos_ids = self.carrinho.keys()
        produtos = Produto.objects.filter(id__in=produtos_ids)
        
        carrinho = self.carrinho.copy()
        
        for produto in produtos:
            carrinho[str(produto.id)]['produto'] = produto
        
        for item in carrinho.values():
            item['preco'] = Decimal(item['preco'])
            item['total_preco'] = item['preco'] * item['quantidade']
            yield item
    
    def __len__(self):
        """
        Retorna o número total de itens no carrinho.
        """
        return sum(item['quantidade'] for item in self.carrinho.values())
    
    def get_total_preco(self):
        """
        Calcula o preço total de todos os itens no carrinho.
        """
        return sum(
            Decimal(item['preco']) * item['quantidade'] 
            for item in self.carrinho.values()
        )
    
    def clear(self):
        """
        Limpa o carrinho da sessão.
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()
