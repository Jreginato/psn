from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('catalogo/', views.catalogo, name='catalogo'),
    path('produto/<slug:slug>/', views.produto_detalhes, name='produto_detalhes'),
    path('vendas/<slug:slug>/', views.produto_vendas, name='produto_vendas'),
    path('comprar/<slug:slug>/', views.criar_pedido, name='criar_pedido'),
]
