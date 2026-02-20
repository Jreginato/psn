"""
Comando para listar pedidos e seus status
Útil para verificar rapidamente os pedidos criados durante os testes

Uso:
    python manage.py listar_pedidos
    python manage.py listar_pedidos --usuario=user@example.com
    python manage.py listar_pedidos --status=pendente
"""
from django.core.management.base import BaseCommand
from produtos.models import Pedido
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Lista todos os pedidos do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            help='Filtrar por email do usuário'
        )
        parser.add_argument(
            '--status',
            type=str,
            choices=['pendente', 'processando', 'aprovado', 'cancelado'],
            help='Filtrar por status do pedido'
        )
        parser.add_argument(
            '--ultimos',
            type=int,
            default=10,
            help='Número de pedidos mais recentes a mostrar (padrão: 10, use 0 para todos)'
        )

    def handle(self, *args, **options):
        # Construir queryset com filtros
        pedidos = Pedido.objects.all().order_by('-criado_em')
        
        # Filtrar por usuário
        if options['usuario']:
            try:
                user = User.objects.get(email=options['usuario'])
                pedidos = pedidos.filter(usuario=user)
                self.stdout.write(f'\n📊 Pedidos do usuário: {user.email}')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f'\n❌ Usuário {options["usuario"]} não encontrado\n'
                ))
                return
        else:
            self.stdout.write('\n📊 Todos os pedidos')
        
        # Filtrar por status
        if options['status']:
            pedidos = pedidos.filter(status=options['status'])
            self.stdout.write(f'   Filtro: status = {options["status"]}')
        
        # Limitar quantidade
        ultimos = options['ultimos']
        if ultimos > 0:
            pedidos = pedidos[:ultimos]
            self.stdout.write(f'   Mostrando: últimos {ultimos} pedidos')
        
        self.stdout.write('\n' + '=' * 100 + '\n')
        
        # Verificar se há pedidos
        if not pedidos.exists():
            self.stdout.write(self.style.WARNING('   Nenhum pedido encontrado.\n'))
            return
        
        # Listar pedidos
        for pedido in pedidos:
            # Ícone baseado no status
            status_icon = {
                'pendente': '⏳',
                'processando': '🔄',
                'aprovado': '✅',
                'cancelado': '❌'
            }.get(pedido.status, '❓')
            
            # Cor baseada no status
            if pedido.status == 'aprovado':
                status_style = self.style.SUCCESS
            elif pedido.status == 'cancelado':
                status_style = self.style.ERROR
            elif pedido.status == 'processando':
                status_style = self.style.WARNING
            else:
                status_style = self.style.NOTICE
            
            # Cabeçalho do pedido
            self.stdout.write(
                f'{status_icon} ' + status_style(f'PEDIDO #{pedido.id}') +
                f' - {pedido.criado_em.strftime("%d/%m/%Y %H:%M")}'
            )
            
            # Informações do pedido
            self.stdout.write(f'   👤 Cliente: {pedido.nome_compra} ({pedido.email_compra})')
            self.stdout.write(f'   💰 Total: R$ {pedido.total:.2f}')
            self.stdout.write(f'   📦 Status: {pedido.status.upper()}')
            
            if pedido.metodo_pagamento:
                self.stdout.write(f'   💳 Pagamento: {pedido.metodo_pagamento}')
            
            if pedido.transaction_id:
                self.stdout.write(f'   🔑 Transaction ID: {pedido.transaction_id}')
            
            if pedido.aprovado_em:
                self.stdout.write(f'   ✅ Aprovado em: {pedido.aprovado_em.strftime("%d/%m/%Y %H:%M")}')
            
            # Listar itens
            itens = pedido.itens.all()
            if itens.exists():
                self.stdout.write('   📋 Itens:')
                for item in itens:
                    self.stdout.write(
                        f'      • {item.nome_produto} '
                        f'(x{item.quantidade}) - R$ {item.subtotal:.2f}'
                    )
            
            # Verificar acessos liberados
            acessos = pedido.acessos.all()
            if acessos.exists():
                self.stdout.write(self.style.SUCCESS('   🔓 Acessos liberados:'))
                for acesso in acessos:
                    self.stdout.write(f'      • {acesso.produto.nome}')
            elif pedido.status == 'aprovado':
                self.stdout.write(self.style.WARNING('   ⚠️  Nenhum acesso liberado ainda'))
            
            self.stdout.write('')  # Linha em branco
        
        # Resumo
        self.stdout.write('=' * 100)
        self.stdout.write(f'\n📈 Resumo:')
        self.stdout.write(f'   Total de pedidos: {pedidos.count()}')
        
        # Estatísticas por status
        for status in ['pendente', 'processando', 'aprovado', 'cancelado']:
            count = Pedido.objects.filter(status=status).count()
            if count > 0:
                icon = {'pendente': '⏳', 'processando': '🔄', 'aprovado': '✅', 'cancelado': '❌'}[status]
                self.stdout.write(f'   {icon} {status.capitalize()}: {count}')
        
        # Valor total
        total_aprovados = sum(p.total for p in Pedido.objects.filter(status='aprovado'))
        if total_aprovados > 0:
            self.stdout.write(f'\n   💵 Total aprovado: R$ {total_aprovados:.2f}')
        
        self.stdout.write('\n💡 Dicas:')
        self.stdout.write('   • Para simular pagamento: python manage.py simular_pagamento <id>')
        self.stdout.write('   • Para filtrar por status: python manage.py listar_pedidos --status=pendente')
        self.stdout.write('   • Para ver todos: python manage.py listar_pedidos --ultimos=0')
        self.stdout.write('')
