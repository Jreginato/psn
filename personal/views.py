from django.shortcuts import render
from produtos.models import Produto, Categoria


def sales_view(request):
    """View da página inicial com produtos reais para acesso direto"""
    produtos = (
        Produto.objects
        .filter(status='publicado')
        .select_related('categoria')
        .order_by('-destaque', 'ordem', '-criado_em')
    )
    categorias = Categoria.objects.filter(ativo=True)

    context = {
        'produtos': produtos,
        'categorias': categorias,
    }
    return render(request, 'sales.html', context)
