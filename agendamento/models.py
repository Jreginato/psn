from django.db import models

class Agendamento(models.Model):
    OBJETIVO_CHOICES = [
        ('emagrecimento', 'Emagrecimento'),
        ('hipertrofia', 'Hipertrofia'),
        ('definicao', 'Definição Muscular'),
        ('performance', 'Performance/Condicionamento'),
        ('outro', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ]

    nome = models.CharField('Nome completo', max_length=200)
    email = models.EmailField('E-mail')
    telefone = models.CharField('Telefone/WhatsApp', max_length=20, help_text='Formato: (11) 99999-9999 ou +5511999999999')
    data_desejada = models.DateField('Data desejada')
    horario_desejado = models.TimeField('Horário desejado')
    objetivo = models.CharField('Objetivo', max_length=20, choices=OBJETIVO_CHOICES)
    mensagem = models.TextField('Mensagem adicional (opcional)', blank=True)
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='pendente')
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome} - {self.data_desejada} às {self.horario_desejado}'
