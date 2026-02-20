# Checklist: Subir Checkout Pro do Mercado Pago para Produção

## 📋 Pré-requisitos
- [ ] Credenciais de produção obtidas no painel do Mercado Pago
- [ ] Domínio com HTTPS configurado (obrigatório)
- [ ] Webhook configurado no painel do MP apontando para seu domínio

---

## 🔧 Alterações no `settings.py`

### 1. Trocar credenciais para produção
```python
# Copie de "Credenciais de produção" no painel do MP
MERCADOPAGO_ACCESS_TOKEN = 'APP_USR-...'  # Token de PRODUÇÃO
MERCADOPAGO_PUBLIC_KEY = 'APP_USR-...'    # Public Key de PRODUÇÃO
```

### 2. Ajustar modo de operação
```python
MERCADOPAGO_MODE = 'prod'          # Alterado de 'test' para 'prod'
MERCADOPAGO_TEST_ONLY = False      # Alterado de True para False
```

### 3. Configurar statement descriptor (opcional)
```python
# Nome que aparece na fatura do cartão do cliente
MERCADOPAGO_STATEMENT_DESCRIPTOR = 'SEU NEGOCIO'  # Max 13 caracteres alfanuméricos
```

### 4. Manter configurações de checkout
```python
MERCADOPAGO_CHECKOUT_POINT = 'init_point'  # Recomendado para produção
MERCADOPAGO_INCLUDE_PAYER = False          # Payer é incluído automaticamente em prod
MERCADOPAGO_PAYER_EMAIL_OVERRIDE = ''      # Deixe vazio para usar email do usuário
```

---

## 🔒 Configurações de Segurança (OBRIGATÓRIO)

Descomente as seguintes linhas em `settings.py`:

```python
# HTTPS obrigatório
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Proteção contra clickjacking
X_FRAME_OPTIONS = 'DENY'

# Prevenir MIME-type sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# Forçar HTTPS por 1 ano (HSTS)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies com SameSite
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
```

---

## 🌐 Webhook no Mercado Pago

1. Acesse: https://www.mercadopago.com.br/developers/panel/app
2. Selecione sua aplicação
3. Vá em **Webhooks**
4. Configure a URL: `https://seudominio.com/checkout/webhook/`
5. Selecione eventos: **Pagamentos**

---

## ✅ Validações de Segurança no `views.py`

### Reativar validações comentadas no webhook

Localize a função `webhook` em `checkout/views.py` e descomente:

```python
# 1. VALIDAÇÃO: Verificar se vem do Mercado Pago (User-Agent)
user_agent = request.META.get('HTTP_USER_AGENT', '')
if 'MercadoPago' not in user_agent:
    security_logger.warning(f'Tentativa de acesso ao webhook sem User-Agent do MP: {user_agent}')
    return HttpResponseForbidden('Invalid User-Agent')

# 2. VALIDAÇÃO: Verificar assinatura x-signature (Mercado Pago v1)
x_signature = request.META.get('HTTP_X_SIGNATURE')
x_request_id = request.META.get('HTTP_X_REQUEST_ID')

if x_signature and x_request_id:
    try:
        parts = dict(part.split('=') for part in x_signature.split(','))
        ts = parts.get('ts')
        hash_signature = parts.get('v1')
        
        body = request.body.decode('utf-8')
        data = json.loads(body)
        data_id = data.get('data', {}).get('id', '')
        manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"
        
        secret = settings.MERCADOPAGO_ACCESS_TOKEN.split('-')[-1]
        calculated_hash = hmac.new(
            secret.encode(),
            manifest.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(calculated_hash, hash_signature):
            security_logger.error(f'Assinatura inválida no webhook! Request ID: {x_request_id}')
            return HttpResponseForbidden('Invalid signature')
            
    except Exception as e:
        security_logger.error(f'Erro ao validar assinatura: {str(e)}')
        pass

# 6. VALIDAÇÃO CRÍTICA: Verificar se o valor pago bate com o pedido
if abs(valor_pago - pedido.total) > Decimal('0.01'):
    security_logger.critical(
        f'ALERTA DE SEGURANÇA: Valor pago ({valor_pago}) diferente do pedido ({pedido.total}) '
        f'para pedido #{pedido_id}, pagamento {payment_id}'
    )
    return HttpResponse(status=200)

# 7. VALIDAÇÃO: Verificar se o pedido não foi aprovado anteriormente
if pedido.status == 'aprovado' and pedido.aprovado_em:
    logger.info(f'Pedido #{pedido_id} já aprovado anteriormente')
    return HttpResponse(status=200)
```

---

## 🧪 Testes antes de subir

- [ ] Teste em ambiente de staging com credenciais de produção
- [ ] Valide fluxo completo: carrinho → checkout → pagamento → retorno → webhook
- [ ] Teste modo convidado (sem login no MP)
- [ ] Teste com usuário logado no MP
- [ ] Valide notificações de webhook
- [ ] Confira logs de segurança

---

## 📊 Monitoramento Pós-Deploy

- [ ] Acompanhe `logs/mercadopago.log` para erros
- [ ] Monitore `logs/security.log` para tentativas suspeitas
- [ ] Valide no painel do MP: https://www.mercadopago.com.br/activities
- [ ] Configure alertas para pagamentos rejeitados/estornos

---

## 🔄 Diferenças: Teste vs Produção

| Aspecto | Teste | Produção |
|---------|-------|----------|
| Credenciais | Teste (podem ser APP_USR) | Produção (APP_USR) |
| Login obrigatório | Sim (usuário teste) | Não (modo convidado ok) |
| Cartões | Cartões de teste (5031...) | Cartões reais |
| Webhooks | localhost/ngrok/túnel | HTTPS público |
| Validações segurança | Podem estar desabilitadas | OBRIGATÓRIAS |
| TEST_ONLY | True | False |

---

## 🚨 Avisos Importantes

1. **NUNCA** misture credenciais de teste e produção
2. **NUNCA** exponha suas credenciais em repositório público
3. **SEMPRE** use variáveis de ambiente em produção
4. **SEMPRE** valide webhooks com assinatura em produção
5. **SEMPRE** valide valor pago vs valor do pedido

---

## 📞 Suporte

- Documentação: https://www.mercadopago.com.br/developers/pt/docs/checkout-pro
- Painel: https://www.mercadopago.com.br/developers/panel/app
- Status da API: https://status.mercadopago.com/
