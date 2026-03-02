"""
Views do Carrinho de Compras
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from produtos.models import Produto
from .carrinho import Carrinho
from .models import Cupom


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


@require_POST
def aplicar_cupom(request):
    """
    Aplica um cupom de desconto ao carrinho (validação 100% no backend).
    """
    carrinho = Carrinho(request)
    codigo = request.POST.get('codigo', '').strip().upper()

    if not codigo:
        messages.error(request, 'Informe o código do cupom.')
        return redirect('carrinho:carrinho_detalhes')

    try:
        cupom = Cupom.objects.get(codigo=codigo)
    except Cupom.DoesNotExist:
        messages.error(request, 'Cupom inválido ou inexistente.')
        return redirect('carrinho:carrinho_detalhes')

    if not cupom.esta_valido:
        if cupom.validade and cupom.validade < timezone.now().date():
            messages.error(request, 'Este cupom está expirado.')
        elif cupom.uso_maximo and cupom.total_usado >= cupom.uso_maximo:
            messages.error(request, 'Este cupom já atingiu o limite de usos.')
        elif not cupom.ativo:
            messages.error(request, 'Este cupom não está ativo.')
        else:
            messages.error(request, 'Cupom inválido.')
        return redirect('carrinho:carrinho_detalhes')

    subtotal = carrinho.get_total_preco()
    if subtotal < cupom.valor_minimo_pedido:
        from django.templatetags.l10n import localize
        messages.error(
            request,
            f'Pedido mínimo para este cupom é R$ {cupom.valor_minimo_pedido:.2f}.'
        )
        return redirect('carrinho:carrinho_detalhes')

    carrinho.set_cupom(cupom)
    desconto = cupom.calcular_desconto(subtotal)
    messages.success(
        request,
        f'Cupom "{cupom.codigo}" aplicado! Desconto de R$ {desconto:.2f}.'
    )
    return redirect('carrinho:carrinho_detalhes')


@require_POST
def remover_cupom(request):
    """
    Remove o cupom aplicado ao carrinho.
    """
    carrinho = Carrinho(request)
    carrinho.clear_cupom()
    messages.info(request, 'Cupom removido.')
    return redirect('carrinho:carrinho_detalhes')

