from decimal import Decimal
from django.conf import settings
from produtos.models import Produto

COUPON_SESSION_KEY = 'cupom_id'


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

    # ─── Métodos de Cupom ────────────────────────────────────────────────────

    @property
    def cupom(self):
        """Retorna o objeto Cupom armazenado na sessão, ou None."""
        from carrinho.models import Cupom
        cupom_id = self.session.get(COUPON_SESSION_KEY)
        if cupom_id:
            try:
                return Cupom.objects.get(id=cupom_id)
            except Cupom.DoesNotExist:
                self.clear_cupom()
        return None

    def set_cupom(self, cupom):
        """Armazena o ID do cupom na sessão."""
        self.session[COUPON_SESSION_KEY] = cupom.id
        self.save()

    def clear_cupom(self):
        """Remove o cupom da sessão."""
        if COUPON_SESSION_KEY in self.session:
            del self.session[COUPON_SESSION_KEY]
            self.save()

    def get_desconto(self):
        """Retorna o valor do desconto baseado no cupom aplicado."""
        cupom = self.cupom
        if cupom and cupom.esta_valido:
            subtotal = self.get_total_preco()
            if subtotal >= cupom.valor_minimo_pedido:
                return cupom.calcular_desconto(subtotal)
        return Decimal('0.00')

    def get_total_com_desconto(self):
        """Retorna o total já com o desconto aplicado."""
        return self.get_total_preco() - self.get_desconto()

    # ─── Métodos do Carrinho ─────────────────────────────────────────────────

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
