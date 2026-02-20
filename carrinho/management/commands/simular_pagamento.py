"""
Comando para simular aprovação de pagamento do Mercado Pago
Útil para testes em desenvolvimento sem precisar do webhook real

Uso:
    python manage.py simular_pagamento <pedido_id>
    python manage.py simular_pagamento <pedido_id> --status=rejected
"""
from django.core.management.base import BaseCommand, CommandError
from django.test import RequestFactory
from produtos.models import Pedido
from carrinho.views import mp_webhook
import json


class Command(BaseCommand):
    help = 'Simula uma notificação de pagamento do Mercado Pago para teste'

    def add_arguments(self, parser):
        parser.add_argument(
            'pedido_id',
            type=int,
            help='ID do pedido a ser atualizado'
        )
        parser.add_argument(
            '--status',
            type=str,
            default='approved',
            choices=['approved', 'pending', 'in_process', 'rejected', 'cancelled'],
            help='Status do pagamento a simular (padrão: approved)'
        )
        parser.add_argument(
            '--valor',
            type=float,
            help='Valor do pagamento (se não especificado, usa o valor do pedido)'
        )

    def handle(self, *args, **options):
        pedido_id = options['pedido_id']
        status = options['status']
        valor = options.get('valor')
        
        # Verificar se o pedido existe
        try:
            pedido = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise CommandError(f'Pedido #{pedido_id} não encontrado')
        
        # Usar valor do pedido se não especificado
        if valor is None:
            valor = float(pedido.total)
        
        # Criar requisição fake simulando o webhook do Mercado Pago
        factory = RequestFactory()
        
        # Dados do webhook simulado
        webhook_data = {
            'type': 'payment',
            'data': {
                'id': f'test_{pedido_id}_{status}'
            },
            'external_reference': str(pedido_id),
            'status': status,
            'transaction_amount': valor
        }
        
        # Criar requisição POST
        request = factory.post(
            '/webhook/mercadopago/',
            data=json.dumps(webhook_data),
            content_type='application/json',
            HTTP_USER_AGENT='MercadoPagoSimulator/1.0 (Development)'
        )
        
        # Processar webhook
        self.stdout.write(self.style.WARNING(
            f'\n🔄 Simulando webhook do Mercado Pago...\n'
        ))
        self.stdout.write(f'   Pedido: #{pedido_id}')
        self.stdout.write(f'   Status: {status}')
        self.stdout.write(f'   Valor: R$ {valor:.2f}')
        self.stdout.write(f'   Status atual do pedido: {pedido.status}\n')
        
        # Executar webhook
        response = mp_webhook(request)
        
        # Recarregar pedido para ver mudanças
        pedido.refresh_from_db()
        
        # Resultado
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Webhook processado com sucesso!\n'
            ))
            self.stdout.write(f'   Novo status do pedido: {pedido.status}')
            
            if pedido.status == 'aprovado':
                self.stdout.write(self.style.SUCCESS(
                    f'   ✅ Pedido APROVADO e acesso aos produtos liberado!'
                ))
                self.stdout.write(f'   Data de aprovação: {pedido.aprovado_em}')
                
                # Listar produtos com acesso liberado
                acessos = pedido.acessos.all()
                if acessos:
                    self.stdout.write('\n   Produtos liberados:')
                    for acesso in acessos:
                        self.stdout.write(f'      • {acesso.produto.nome}')
            
            elif pedido.status == 'processando':
                self.stdout.write(self.style.WARNING(
                    f'   ⏳ Pagamento em processamento'
                ))
            
            elif pedido.status == 'cancelado':
                self.stdout.write(self.style.ERROR(
                    f'   ❌ Pagamento cancelado/rejeitado'
                ))
            
            self.stdout.write('\n')
            
        else:
            self.stdout.write(self.style.ERROR(
                f'\n❌ Erro ao processar webhook! Status: {response.status_code}\n'
            ))
        
        # Dicas úteis
        self.stdout.write(self.style.NOTICE(
            '\n💡 Dicas de teste:\n'
            '   • Para aprovar: python manage.py simular_pagamento <id>\n'
            '   • Para rejeitar: python manage.py simular_pagamento <id> --status=rejected\n'
            '   • Para pendente: python manage.py simular_pagamento <id> --status=pending\n'
            '   • Ver pedidos: python manage.py shell -c "from produtos.models import Pedido; [print(f\'#{p.id}: {p.status}\') for p in Pedido.objects.all()]"\n'
        ))
