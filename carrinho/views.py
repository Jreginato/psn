"""
Views do Carrinho de Compras
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from produtos.models import Produto
from .carrinho import Carrinho


def carrinho_detalhes(request):
    """
    Exibe o carrinho de compras.
    """
    carrinho = Carrinho(request)
    return render(request, 'carrinho/detalhes.html', {'carrinho': carrinho})


@require_POST
def carrinho_add(request, produto_id):
    """
    Adiciona um produto ao carrinho.
    """
    carrinho = Carrinho(request)
    produto = get_object_or_404(Produto, id=produto_id, status='publicado')
    
    # Como são produtos digitais, geralmente não duplicamos (quantidade sempre 1)
    carrinho.add(produto=produto, quantidade=1, substituir_quantidade=True)
    
    messages.success(request, f'{produto.nome} foi adicionado ao carrinho!')
    
    # Redireciona de volta para a página de origem
    return redirect(request.META.get('HTTP_REFERER', 'produtos:catalogo'))


@require_POST
def carrinho_remove(request, produto_id):
    """
    Remove um produto do carrinho.
    """
    carrinho = Carrinho(request)
    produto = get_object_or_404(Produto, id=produto_id)
    
    carrinho.remove(produto)
    
    messages.info(request, f'{produto.nome} foi removido do carrinho.')
    
    return redirect('carrinho:carrinho_detalhes')


def carrinho_clear(request):
    """
    Limpa todos os itens do carrinho.
    """
    carrinho = Carrinho(request)
    carrinho.clear()
    
    messages.info(request, 'O carrinho foi esvaziado.')
    
    return redirect('carrinho:carrinho_detalhes')
