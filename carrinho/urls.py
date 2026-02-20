"""
URLs do Carrinho de Compras
"""
from django.urls import path
from . import views

app_name = 'carrinho'

urlpatterns = [
    # Carrinho
    path('', views.carrinho_detalhes, name='carrinho_detalhes'),
    path('add/<int:produto_id>/', views.carrinho_add, name='carrinho_add'),
    path('remove/<int:produto_id>/', views.carrinho_remove, name='carrinho_remove'),
    path('clear/', views.carrinho_clear, name='carrinho_clear'),
]
