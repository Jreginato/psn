from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Cupom(models.Model):
    TIPO_CHOICES = [
        ('percentual', 'Percentual (%)'),
        ('fixo', 'Valor Fixo (R$)'),
    ]

    codigo = models.CharField(
        'Código',
        max_length=50,
        unique=True,
        help_text='Ex: BEMVINDO10, NATAL20. Será salvo em maiúsculo.'
    )
    tipo = models.CharField(
        'Tipo de Desconto',
        max_length=10,
        choices=TIPO_CHOICES,
        default='percentual'
    )
    valor = models.DecimalField(
        'Valor do Desconto',
        max_digits=10,
        decimal_places=2,
        help_text='Para percentual: 10 = 10%. Para fixo: 10 = R$ 10,00'
    )
    valor_minimo_pedido = models.DecimalField(
        'Valor Mínimo do Pedido',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Pedido mínimo para usar o cupom. 0 = sem restrição.'
    )
    ativo = models.BooleanField('Ativo', default=True)
    validade = models.DateTimeField(
        'Válido até',
        null=True,
        blank=True,
        help_text='Deixe em branco para sem validade.'
    )
    uso_maximo = models.PositiveIntegerField(
        'Uso Máximo',
        null=True,
        blank=True,
        help_text='Quantas vezes pode ser usado no total. Deixe em branco para ilimitado.'
    )
    total_usado = models.PositiveIntegerField(
        'Total de Usos',
        default=0,
        editable=False
    )
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Cupôm'
        verbose_name_plural = 'Cupõns'
        ordering = ['-criado_em']

    def __str__(self):
        if self.tipo == 'percentual':
            return f'{self.codigo} — {self.valor}% de desconto'
        return f'{self.codigo} — R$ {self.valor} de desconto'

    def save(self, *args, **kwargs):
        self.codigo = self.codigo.upper().strip()
        super().save(*args, **kwargs)

    def clean(self):
        if self.tipo == 'percentual' and self.valor > 100:
            raise ValidationError({'valor': 'Desconto percentual não pode ser maior que 100%.'})
        if self.valor <= 0:
            raise ValidationError({'valor': 'O valor do desconto deve ser maior que zero.'})

    @property
    def esta_valido(self):
        """Retorna True se o cupom pode ser usado agora."""
        if not self.ativo:
            return False
        if self.validade and timezone.now() > self.validade:
            return False
        if self.uso_maximo is not None and self.total_usado >= self.uso_maximo:
            return False
        return True

    def calcular_desconto(self, subtotal):
        """Calcula o valor do desconto para o subtotal informado."""
        subtotal = Decimal(str(subtotal))
        if self.tipo == 'percentual':
            desconto = (subtotal * self.valor / Decimal('100')).quantize(Decimal('0.01'))
        else:
            desconto = min(self.valor, subtotal)
        return desconto
