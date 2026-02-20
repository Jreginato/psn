from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produto, Categoria, AcessoProduto, Pedido, ItemPedido


def catalogo(request):
    """Catálogo de produtos digitais"""
    produtos = Produto.objects.filter(status='publicado').select_related('categoria')
    categorias = Categoria.objects.filter(ativo=True)
    
    # Filtrar por categoria se especificado
    categoria_slug = request.GET.get('categoria')
    if categoria_slug:
        produtos = produtos.filter(categoria__slug=categoria_slug)
    
    context = {
        'produtos': produtos,
        'categorias': categorias,
        'categoria_atual': categoria_slug
    }
    return render(request, 'produtos/catalogo.html', context)


def produto_detalhes(request, slug):
    """Detalhes de um produto específico"""
    produto = get_object_or_404(
        Produto.objects.select_related('categoria').prefetch_related('conteudos'),
        slug=slug,
        status='publicado'
    )
    
    # Verificar se usuário tem acesso (se logado)
    tem_acesso = False
    if request.user.is_authenticated:
        tem_acesso = AcessoProduto.objects.filter(
            usuario=request.user,
            produto=produto,
            ativo=True
        ).exists()
    
    context = {
        'produto': produto,
        'tem_acesso': tem_acesso
    }
    return render(request, 'produtos/produto_detalhes.html', context)


def produto_vendas(request, slug):
    """Página de vendas dinâmica do produto"""
    produto = get_object_or_404(
        Produto.objects.select_related('categoria'),
        slug=slug,
        status='publicado'
    )
    
    context = {
        'produto': produto,
    }
    return render(request, 'produtos/produto_vendas.html', context)


@login_required
def criar_pedido(request, slug):
    """Criar pedido para um produto"""
    if request.method != 'POST':
        return redirect('produtos:produto_vendas', slug=slug)
    
    produto = get_object_or_404(Produto, slug=slug, status='publicado')
    
    # Verificar se usuário já tem acesso a este produto
    if AcessoProduto.objects.filter(usuario=request.user, produto=produto, ativo=True).exists():
        messages.info(request, 'Você já possui este produto!')
        return redirect('dashboard:home')
    
    # Criar pedido
    pedido = Pedido.objects.create(
        usuario=request.user,
        total=produto.preco_promocional if produto.preco_promocional else produto.preco,
        status='pendente'
    )
    
    # Criar item do pedido
    ItemPedido.objects.create(
        pedido=pedido,
        produto=produto,
        preco=produto.preco_promocional if produto.preco_promocional else produto.preco
    )
    
    messages.success(request, f'Pedido #{pedido.id} criado com sucesso! Aguardando pagamento.')
    return redirect('dashboard:pedidos')
