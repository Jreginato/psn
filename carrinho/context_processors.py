from .carrinho import Carrinho


def carrinho(request):
    """
    Context processor para disponibilizar o carrinho em todos os templates.
    """
    return {'carrinho': Carrinho(request)}
