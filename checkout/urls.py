"""
URLs do Checkout
"""
from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    # Página de checkout
    path('', views.checkout, name='checkout'),
    
    # Processar pedido e redirecionar para Mercado Pago
    path('processar/', views.processar_pedido, name='processar_pedido'),
    
    # URLs de retorno do Mercado Pago
    path('sucesso/<int:pedido_id>/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('falha/<int:pedido_id>/', views.pagamento_falha, name='pagamento_falha'),
    path('pendente/<int:pedido_id>/', views.pagamento_pendente, name='pagamento_pendente'),
    
    # Webhook do Mercado Pago
    path('webhook/', views.webhook, name='webhook'),
]
