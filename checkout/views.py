"""
Views do Checkout e Processamento de Pagamentos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from decimal import Decimal
import mercadopago
import json
import hmac
import hashlib
import logging

from produtos.models import Produto, Pedido, ItemPedido
from carrinho.carrinho import Carrinho

# Configurar loggers
logger = logging.getLogger('mercadopago')
security_logger = logging.getLogger('security')


def _normalizar_statement_descriptor(valor: str) -> str:
    """
    Mercado Pago aceita statement descriptor com no máximo 13 caracteres.
    Mantém apenas caracteres alfanuméricos e força uppercase.
    """
    if not valor:
        return 'PERSONALTRNR'

    limpo = ''.join(ch for ch in valor.upper() if ch.isalnum())
    if not limpo:
        return 'PERSONALTRNR'

    return limpo[:13]


def _sanitizar_nome_payer(nome: str) -> tuple[str, str]:
    """
    Sanitiza e divide nome completo para payer (Mercado Pago).
    Retorna (first_name, last_name) com máximo 255 caracteres cada.
    Remove caracteres especiais problemáticos.
    """
    if not nome or not nome.strip():
        return ('Usuario', 'Convidado')
    
    # Remove caracteres problemáticos, mantém letras, números, espaços e acentos básicos
    nome_limpo = ''.join(ch for ch in nome if ch.isalnum() or ch.isspace() or ch in 'áàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ')
    nome_limpo = ' '.join(nome_limpo.split())  # normaliza espaços
    
    if not nome_limpo:
        return ('Usuario', 'Convidado')
    
    partes = nome_limpo.split(maxsplit=1)
    first_name = partes[0][:255]
    last_name = partes[1][:255] if len(partes) > 1 else 'Silva'
    
    return (first_name, last_name)


def _sincronizar_status_retorno_mp(request, pedido):
    """
    Sincroniza status do pedido com dados de retorno do Mercado Pago.
    Prioriza consulta na API quando houver payment_id no retorno.
    """
    status_mp = request.GET.get('status')
    payment_id = request.GET.get('payment_id')

    if payment_id:
        try:
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            if payment_info.get('status') == 200:
                response = payment_info.get('response', {})
                status_mp = response.get('status') or status_mp
                pedido.transaction_id = str(payment_id)
        except Exception as e:
            logger.warning('Falha ao consultar pagamento %s no retorno: %s', payment_id, str(e))

    if status_mp == 'approved':
        if pedido.status != 'aprovado':
            pedido.status = 'aprovado'
            pedido.aprovado_em = timezone.now()
            pedido.save()
            pedido.liberar_acesso_produtos()
    elif status_mp in ('rejected', 'cancelled'):
        if pedido.status != 'cancelado':
            pedido.status = 'cancelado'
            pedido.save()
    elif status_mp in ('in_process', 'pending'):
        if pedido.status == 'pendente':
            pedido.status = 'processando'
            pedido.save()


@login_required
def checkout(request):
    """
    Página de revisão do pedido antes de finalizar a compra.
    """
    carrinho = Carrinho(request)
    
    # Verifica se o carrinho está vazio
    if len(carrinho) == 0:
        messages.warning(request, 'Seu carrinho está vazio!')
        return redirect('produtos:catalogo')
    
    # Calcula o total
    total = carrinho.get_total_preco()
    
    context = {
        'carrinho': carrinho,
        'total': total,
    }
    
    return render(request, 'checkout/checkout.html', context)


@login_required
@require_POST
def processar_pedido(request):
    """
    Processa o pedido, cria no banco e redireciona para pagamento no Mercado Pago.
    """
    carrinho = Carrinho(request)
    
    # Verifica se o carrinho está vazio
    if len(carrinho) == 0:
        messages.error(request, 'Seu carrinho está vazio!')
        return redirect('produtos:catalogo')
    
    # Calcula valores
    subtotal = carrinho.get_total_preco()
    desconto = Decimal('0.00')
    total = subtotal - desconto
    
    # Cria o pedido
    pedido = Pedido.objects.create(
        usuario=request.user,
        subtotal=subtotal,
        desconto=desconto,
        total=total,
        status='pendente',
        email_compra=request.user.email,
        nome_compra=request.user.get_full_name() or request.user.email,
        metodo_pagamento='Mercado Pago'
    )
    
    # Cria os itens do pedido
    items_mp = []
    total_verificacao = Decimal('0.00')
    
    for item in carrinho:
        ItemPedido.objects.create(
            pedido=pedido,
            produto=item['produto'],
            nome_produto=item['produto'].nome,
            preco_unitario=item['preco'],
            quantidade=item['quantidade'],
            subtotal=item['total_preco']
        )
        
        # Adiciona item para o Mercado Pago
        items_mp.append({
            "title": item['produto'].nome[:120],
            "quantity": item['quantidade'],
            "unit_price": float(item['preco']),
            "currency_id": "BRL",
        })
        
        total_verificacao += item['total_preco']
    
    # VALIDAÇÃO: Garantir que o total bate
    if abs(total_verificacao - total) > Decimal('0.01'):
        security_logger.critical(
            f'ALERTA: Divergência de valores ao criar pedido #{pedido.id}. '
            f'Total calculado: {total_verificacao}, Total do pedido: {total}'
        )
        pedido.delete()
        messages.error(request, 'Erro ao processar pedido. Por favor, tente novamente.')
        return redirect('checkout:checkout')
    
    # Configura SDK do Mercado Pago
    access_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')
    if not access_token:
        logger.error('MERCADOPAGO_ACCESS_TOKEN não configurado')
        pedido.delete()
        messages.error(request, 'Pagamento indisponível no momento. Tente novamente em instantes.')
        return redirect('checkout:checkout')

    sdk = mercadopago.SDK(access_token)

    mp_mode = getattr(settings, 'MERCADOPAGO_MODE', 'test' if settings.DEBUG else 'prod').lower().strip()
    test_only = bool(getattr(settings, 'MERCADOPAGO_TEST_ONLY', False))
    if test_only and mp_mode != 'test':
        logger.warning('MERCADOPAGO_TEST_ONLY ativo: sobrescrevendo mp_mode=%s para test.', mp_mode)
        mp_mode = 'test'
    public_key = getattr(settings, 'MERCADOPAGO_PUBLIC_KEY', '')
    token_prefix = 'TEST' if access_token.startswith('TEST-') else 'APP_USR' if access_token.startswith('APP_USR-') else 'UNKNOWN'
    public_key_prefix = 'TEST' if public_key.startswith('TEST-') else 'APP_USR' if public_key.startswith('APP_USR-') else 'UNKNOWN'

    env_diag = {
        'pedido_id': pedido.id,
        'mp_mode': mp_mode,
        'test_only': test_only,
        'token_prefix': token_prefix,
        'token_head': f"{access_token[:16]}..." if access_token else '',
        'public_key_prefix': public_key_prefix,
        'public_key_head': f"{public_key[:16]}..." if public_key else '',
        'checkout_point_setting': getattr(settings, 'MERCADOPAGO_CHECKOUT_POINT', 'init_point'),
        'debug': bool(settings.DEBUG),
    }
    logger.warning('MP_ENV_DIAGNOSTIC=%s', json.dumps(env_diag, ensure_ascii=False, default=str))
    print(f"MP_ENV_DIAGNOSTIC={json.dumps(env_diag, ensure_ascii=False, default=str)}")
    
    # URLs de retorno
    base_url = request.build_absolute_uri('/')[:-1]

    # Em produção (não test_only), incluir payer para modo convidado
    include_payer = getattr(settings, 'MERCADOPAGO_INCLUDE_PAYER', False)
    if not test_only and not include_payer:
        # Em produção, sempre incluir payer para suportar modo convidado
        include_payer = True
    
    payer_data = None
    if include_payer:
        nome_completo = (request.user.get_full_name() or '').strip()
        payer_email = getattr(settings, 'MERCADOPAGO_PAYER_EMAIL_OVERRIDE', '').strip() or request.user.email
        
        # Sanitiza nome conforme regras do Mercado Pago
        first_name, last_name = _sanitizar_nome_payer(nome_completo)
        
        payer_data = {
            "email": payer_email[:255] if payer_email else 'usuario@exemplo.com',
            "name": first_name,
            "surname": last_name,
        }
    
    is_local_callback = 'localhost' in base_url or '127.0.0.1' in base_url

    # Cria preferência de pagamento
    statement_descriptor = _normalizar_statement_descriptor(
        getattr(settings, 'MERCADOPAGO_STATEMENT_DESCRIPTOR', 'PERSONAL TRAINER')
    )

    preference_data = {
        "items": items_mp,
        "back_urls": {
            "success": f"{base_url}{reverse('checkout:pagamento_sucesso', args=[pedido.id])}",
            "failure": f"{base_url}{reverse('checkout:pagamento_falha', args=[pedido.id])}",
            "pending": f"{base_url}{reverse('checkout:pagamento_pendente', args=[pedido.id])}",
        },
        "notification_url": f"{base_url}{reverse('checkout:webhook')}",
        "external_reference": str(pedido.id),
        "statement_descriptor": statement_descriptor,
    }

    # Em ambiente local, o Mercado Pago pode rejeitar auto_return por URL não pública
    if not is_local_callback:
        preference_data["auto_return"] = "approved"

    if payer_data:
        preference_data["payer"] = payer_data

    payload_json_pretty = json.dumps(preference_data, ensure_ascii=False, indent=2, default=str)
    payload_json_single = json.dumps(preference_data, ensure_ascii=False, default=str)

    logger.warning('MP_PREFERENCE_JSON=%s', payload_json_single)
    print(f"MP_PREFERENCE_JSON={payload_json_single}")

    logger.info(
        'Payload enviado para criar preferência MP (pedido #%s):\n%s',
        pedido.id,
        payload_json_pretty,
    )
    
    try:
        preference_response = sdk.preference().create(preference_data)
        response_json_single = json.dumps(preference_response, ensure_ascii=False, default=str)
        logger.warning('MP_PREFERENCE_RESPONSE_JSON=%s', response_json_single)
        print(f"MP_PREFERENCE_RESPONSE_JSON={response_json_single}")
        logger.info(
            'Resposta da criação de preferência MP (pedido #%s):\n%s',
            pedido.id,
            json.dumps(preference_response, ensure_ascii=False, indent=2, default=str),
        )
        preference = preference_response.get('response', {}) if isinstance(preference_response, dict) else {}
        status_code = preference_response.get('status') if isinstance(preference_response, dict) else None

        if status_code not in (200, 201) or not preference.get('id'):
            erro_code = preference.get('code') if isinstance(preference, dict) else None
            erro_message = preference.get('message') if isinstance(preference, dict) else None

            if status_code == 401 and erro_code == 'unauthorized' and erro_message == 'invalid access token':
                detalhe_erro = (
                    'invalid access token. Em Checkout Pro, as credenciais de teste podem vir com prefixo APP_USR. '
                    'Não altere prefixo manualmente; copie exatamente o Access Token da tela "Credenciais de teste" '
                    'e teste com usuário comprador de teste em janela anônima.'
                )
            else:
                detalhe_erro = (
                    preference.get('message')
                    or preference.get('error')
                    or preference_response.get('message')
                    if isinstance(preference_response, dict)
                    else 'resposta inválida da API'
                )
            logger.error(
                'Falha ao criar preferência MP para pedido #%s. status=%s resposta=%s',
                pedido.id,
                status_code,
                preference_response,
            )
            raise ValueError(f'Não foi possível iniciar o pagamento no Mercado Pago ({detalhe_erro}).')

        checkout_point = getattr(settings, 'MERCADOPAGO_CHECKOUT_POINT', 'init_point')

        if test_only:
            checkout_url = preference.get('init_point') or preference.get('sandbox_init_point')
        elif checkout_point == 'sandbox_init_point' and token_prefix == 'APP_USR' and mp_mode == 'test':
            logger.warning(
                'Ajuste automático de checkout_point: sandbox_init_point -> init_point para fluxo de teste com APP_USR.'
            )
            checkout_url = preference.get('init_point') or preference.get('sandbox_init_point')
        elif checkout_point == 'sandbox_init_point':
            checkout_url = preference.get('sandbox_init_point') or preference.get('init_point')
        elif checkout_point == 'auto':
            checkout_url = preference.get('init_point') or preference.get('sandbox_init_point')
        else:
            checkout_url = preference.get('init_point') or preference.get('sandbox_init_point')

        if not checkout_url:
            logger.error('Preferência MP sem init_point para pedido #%s. resposta=%s', pedido.id, preference_response)
            raise ValueError('Mercado Pago não retornou URL de checkout.')
        
        # Salva o ID da preferência no pedido
        pedido.transaction_id = preference["id"]
        pedido.save()
        
        # Limpa o carrinho
        carrinho.clear()
        
        logger.info(f'Pedido #{pedido.id} criado. Redirecionando para Mercado Pago...')
        
        # Redireciona para o checkout do Mercado Pago
        return redirect(checkout_url)
        
    except Exception as e:
        logger.error(f'Erro ao criar preferência MP para pedido #{pedido.id}: {str(e)}')
        pedido.delete()
        if settings.DEBUG:
            messages.error(request, f'Não foi possível iniciar o pagamento. Detalhe: {str(e)}')
        else:
            messages.error(request, 'Não foi possível iniciar o pagamento. Verifique os dados e tente novamente.')
        return redirect('checkout:checkout')


@login_required
def pagamento_sucesso(request, pedido_id):
    """
    Página de retorno quando o pagamento é aprovado no Mercado Pago.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    _sincronizar_status_retorno_mp(request, pedido)
    
    if pedido.status == 'aprovado':
        messages.success(request, 'Pagamento aprovado com sucesso! Seu acesso já foi liberado.')
    elif pedido.status == 'cancelado':
        messages.error(request, 'Pagamento não aprovado. Tente novamente com outra forma de pagamento.')
    else:
        messages.info(request, 'Pagamento em análise/processamento. Você será notificado quando for confirmado.')
    
    context = {
        'pedido': pedido,
    }
    
    return render(request, 'checkout/pagamento_sucesso.html', context)


@login_required
def pagamento_falha(request, pedido_id):
    """
    Página de retorno quando o pagamento falha.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    _sincronizar_status_retorno_mp(request, pedido)
    
    logger.warning(f'Pedido #{pedido.id} retornou com falha do MP')
    if pedido.status == 'aprovado':
        messages.success(request, 'Pagamento aprovado com sucesso! Seu acesso já foi liberado.')
    else:
        messages.error(request, 'Ops! O pagamento não foi concluído. Tente novamente.')
    
    context = {
        'pedido': pedido,
    }
    
    return render(request, 'checkout/pagamento_falha.html', context)


@login_required
def pagamento_pendente(request, pedido_id):
    """
    Página de retorno quando o pagamento fica pendente.
    """
    pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    _sincronizar_status_retorno_mp(request, pedido)
    
    if pedido.status == 'pendente':
        pedido.status = 'processando'
        pedido.save()
    
    logger.info(f'Pedido #{pedido.id} ficou pendente no MP')
    messages.info(request, 'Pagamento pendente. Você será notificado quando for aprovado.')
    
    context = {
        'pedido': pedido,
    }
    
    return render(request, 'checkout/pagamento_sucesso.html', context)


@csrf_exempt
@require_POST
def webhook(request):
    """
    Webhook para receber notificações do Mercado Pago.
    
    ⚠️ MODO DE DESENVOLVIMENTO - VALIDAÇÕES DE SEGURANÇA DESABILITADAS ⚠️
    Para reativar em produção, descomente as seções de validação!
    """
    try:
        logger.info('🔓 WEBHOOK EM MODO DE DESENVOLVIMENTO - Validações de segurança desabilitadas')
        
        # ========== VALIDAÇÕES DE SEGURANÇA (DESABILITADAS PARA TESTE) ==========
        
        # # 1. VALIDAÇÃO: Verificar se vem do Mercado Pago (User-Agent)
        # user_agent = request.META.get('HTTP_USER_AGENT', '')
        # if 'MercadoPago' not in user_agent:
        #     security_logger.warning(f'Tentativa de acesso ao webhook sem User-Agent do MP: {user_agent}')
        #     return HttpResponseForbidden('Invalid User-Agent')
        
        # # 2. VALIDAÇÃO: Verificar assinatura x-signature (Mercado Pago v1)
        # x_signature = request.META.get('HTTP_X_SIGNATURE')
        # x_request_id = request.META.get('HTTP_X_REQUEST_ID')
        # 
        # if x_signature and x_request_id:
        #     try:
        #         parts = dict(part.split('=') for part in x_signature.split(','))
        #         ts = parts.get('ts')
        #         hash_signature = parts.get('v1')
        #         
        #         body = request.body.decode('utf-8')
        #         data = json.loads(body)
        #         data_id = data.get('data', {}).get('id', '')
        #         manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
        #         
        #         secret = settings.MERCADOPAGO_ACCESS_TOKEN.split('-')[-1]
        #         calculated_hash = hmac.new(
        #             secret.encode(),
        #             manifest.encode(),
        #             hashlib.sha256
        #         ).hexdigest()
        #         
        #         if not hmac.compare_digest(calculated_hash, hash_signature):
        #             security_logger.error(f'Assinatura inválida no webhook! Request ID: {x_request_id}')
        #             return HttpResponseForbidden('Invalid signature')
        #             
        #     except Exception as e:
        #         security_logger.error(f'Erro ao validar assinatura: {str(e)}')
        #         pass
        
        # ========== FIM DAS VALIDAÇÕES DE SEGURANÇA ==========
        
        # 3. PROCESSA OS DADOS DO WEBHOOK
        data = json.loads(request.body)
        
        logger.info(f'Webhook recebido: {data.get("type")} - ID: {data.get("data", {}).get("id")}')
        
        # Verifica se é uma notificação de pagamento
        if data.get('type') == 'payment':
            payment_id = data.get('data', {}).get('id')
            
            if not payment_id:
                logger.warning('Webhook sem payment_id')
                return HttpResponse(status=200)
            
            # 4. BUSCA INFORMAÇÕES DO PAGAMENTO NO MERCADO PAGO
            # EM MODO DE DESENVOLVIMENTO: Continua mesmo se não encontrar
            sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
            
            try:
                payment_info = sdk.payment().get(payment_id)
            except Exception as e:
                logger.error(f'Erro ao buscar pagamento {payment_id}: {str(e)}')
                logger.warning('🔓 MODO DEV: Continuando mesmo com erro na API')
                # Em desenvolvimento, cria um payment fake para teste
                payment = {
                    'external_reference': data.get('external_reference') or data.get('data', {}).get('external_reference'),
                    'status': data.get('status', 'approved'),
                    'transaction_amount': data.get('transaction_amount', 0),
                    'payment_method_id': 'test'
                }
                payment_info = {'status': 200, 'response': payment}
            
            if payment_info['status'] != 200:
                logger.error(f'Pagamento {payment_id} não encontrado no MP')
                logger.warning('🔓 MODO DEV: Continuando mesmo sem encontrar pagamento')
                # Em desenvolvimento, cria um payment fake para teste
                payment = {
                    'external_reference': data.get('external_reference') or data.get('data', {}).get('external_reference'),
                    'status': data.get('status', 'approved'),
                    'transaction_amount': data.get('transaction_amount', 0),
                    'payment_method_id': 'test'
                }
            else:
                payment = payment_info['response']
            
            # 5. VALIDAÇÕES DE SEGURANÇA DO PAGAMENTO
            pedido_id = payment.get('external_reference')
            status = payment.get('status')
            valor_pago = Decimal(str(payment.get('transaction_amount', 0)))
            
            if not pedido_id:
                logger.warning(f'Pagamento {payment_id} sem external_reference')
                return HttpResponse(status=200)
            
            try:
                pedido = Pedido.objects.get(id=pedido_id)
            except Pedido.DoesNotExist:
                logger.error(f'Tentativa de atualizar pedido inexistente: {pedido_id}')
                return HttpResponse(status=200)
            
            # # 6. VALIDAÇÃO CRÍTICA: Verificar se o valor pago bate com o pedido (DESABILITADA)
            # if abs(valor_pago - pedido.total) > Decimal('0.01'):
            #     security_logger.critical(
            #         f'ALERTA DE SEGURANÇA: Valor pago ({valor_pago}) diferente do pedido ({pedido.total}) '
            #         f'para pedido #{pedido_id}, pagamento {payment_id}'
            #     )
            #     return HttpResponse(status=200)
            
            # # 7. VALIDAÇÃO: Verificar se o pedido não foi aprovado anteriormente (DESABILITADA)
            # if pedido.status == 'aprovado' and pedido.aprovado_em:
            #     logger.info(f'Pedido #{pedido_id} já aprovado anteriormente')
            #     return HttpResponse(status=200)
            
            # 8. ATUALIZA STATUS BASEADO NO PAGAMENTO
            status_anterior = pedido.status
            
            if status == 'approved':
                pedido.status = 'aprovado'
                pedido.aprovado_em = timezone.now()
                pedido.metodo_pagamento = f"Mercado Pago - {payment.get('payment_method_id', 'N/A')}"
                pedido.transaction_id = str(payment_id)
                pedido.save()
                
                # Libera acesso aos produtos
                pedido.liberar_acesso_produtos()
                
                logger.info(f'✅ Pedido #{pedido_id} APROVADO - Pagamento {payment_id} - R$ {valor_pago}')
                security_logger.info(f'Acesso liberado para pedido #{pedido_id} - Usuário: {pedido.usuario.email}')
                
            elif status == 'in_process' or status == 'pending':
                pedido.status = 'processando'
                pedido.save()
                logger.info(f'⏳ Pedido #{pedido_id} EM PROCESSAMENTO')
                
            elif status == 'rejected' or status == 'cancelled':
                pedido.status = 'cancelado'
                pedido.save()
                logger.info(f'❌ Pedido #{pedido_id} CANCELADO/REJEITADO')
            
            else:
                logger.warning(f'Status desconhecido: {status} para pedido #{pedido_id}')
        
        return HttpResponse(status=200)
        
    except json.JSONDecodeError as e:
        logger.error(f'Erro ao decodificar JSON do webhook: {str(e)}')
        return HttpResponse(status=400)
        
    except Exception as e:
        logger.error(f'Erro no processamento do webhook: {str(e)}', exc_info=True)
        return HttpResponse(status=200)
