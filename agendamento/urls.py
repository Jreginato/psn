from django.urls import path
from . import views

app_name = 'agendamento'

urlpatterns = [
    path('', views.agendar, name='agendar'),
    path('sucesso/', views.agendamento_sucesso, name='sucesso'),
]
