from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('meus-produtos/', views.meus_produtos, name='meus_produtos'),
    path('produto/<slug:slug>/', views.produto_detalhes, name='produto_detalhes'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('perfil/', views.perfil, name='perfil'),
    
    # Consultoria Online
    path('consultoria/treino/', views.consultoria_treino, name='consultoria_treino'),
    path('consultoria/treino/pdf/', views.consultoria_treino_pdf, name='consultoria_treino_pdf'),
    path('consultoria/treino/excel/', views.consultoria_treino_excel, name='consultoria_treino_excel'),
    path('consultoria/plano-alimentar/', views.consultoria_plano_alimentar, name='consultoria_plano_alimentar'),
    path('consultoria/medicacao/', views.consultoria_medicacao, name='consultoria_medicacao'),
]
