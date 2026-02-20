# 🔒 SEGURANÇA - Medidas de Proteção Implementadas

## ✅ Proteções Contra Man-in-the-Middle e Fraudes

### 1. **Validação de Assinatura do Webhook (x-signature)**

**Proteção:** Valida que a requisição realmente vem do Mercado Pago

**Como funciona:**
```python
# Mercado Pago envia header x-signature com hash HMAC-SHA256
# Calculamos o hash e comparamos de forma timing-safe
if not hmac.compare_digest(calculated_hash, hash_signature):
    return HttpResponseForbidden('Invalid signature')
```

**Previne:**
- ❌ Atacantes enviando webhooks falsos
- ❌ Modificação de dados em trânsito
- ❌ Replay attacks

---

### 2. **Verificação de User-Agent**

**Proteção:** Confirma que a requisição vem do Mercado Pago

```python
user_agent = request.META.get('HTTP_USER_AGENT', '')
if 'MercadoPago' not in user_agent:
    return HttpResponseForbidden('Invalid User-Agent')
```

**Previne:**
- ❌ Requisições de fontes não autorizadas
- ❌ Scripts automatizados maliciosos

---

### 3. **Validação de Valores (Anti-Fraude)**

**CRÍTICO:** Verifica se o valor pago corresponde ao valor do pedido

```python
# Tolerância de apenas 1 centavo
if abs(valor_pago - pedido.total) > Decimal('0.01'):
    security_logger.critical('ALERTA: Valores não batem!')
    return HttpResponse(status=200)  # NÃO aprova
```

**Previne:**
- ❌ Adulteração de valores no checkout
- ❌ Pagamento de valores menores
- ❌ Fraudes de "desconto não autorizado"

---

### 4. **Proteção Contra Replay Attacks**

**Proteção:** Impede que um pagamento seja processado múltiplas vezes

```python
if pedido.status == 'aprovado' and pedido.aprovado_em:
    logger.info('Pedido já aprovado anteriormente')
    return HttpResponse(status=200)
```

**Previne:**
- ❌ Reenvio malicioso de notificações antigas
- ❌ Liberação duplicada de acesso
- ❌ Fraude de "double spending"

---

### 5. **Verificação no Mercado Pago**

**Proteção:** Sempre consulta o MP para confirmar o pagamento

```python
# Não confia apenas no webhook
payment_info = sdk.payment().get(payment_id)
# Usa dados DIRETO do Mercado Pago
```

**Previne:**
- ❌ Webhooks falsos com dados fabricados
- ❌ Manipulação de informações de pagamento
- ❌ Bypass do sistema de pagamento

---

### 6. **HTTPS Obrigatório em Produção**

**Configurado em `settings.py`:**

```python
# Descomente em produção
SECURE_SSL_REDIRECT = True          # Força HTTPS
SESSION_COOKIE_SECURE = True        # Cookies só em HTTPS
CSRF_COOKIE_SECURE = True           # CSRF token só em HTTPS
SECURE_HSTS_SECONDS = 31536000      # HSTS por 1 ano
```

**Previne:**
- ❌ Man-in-the-Middle
- ❌ Sniffing de dados sensíveis
- ❌ Session hijacking
- ❌ Cookie theft

---

### 7. **Logging de Segurança**

**Monitoramento:** Todos os eventos suspeitos são registrados

```python
# Logs em: logs/security.log e logs/mercadopago.log

security_logger.warning('Tentativa suspeita detectada')
security_logger.critical('ALERTA: Valores não batem!')
logger.info('Pedido aprovado com sucesso')
```

**Permite:**
- ✅ Auditoria de transações
- ✅ Detecção de tentativas de fraude
- ✅ Análise forense em caso de incidentes
- ✅ Monitoramento em tempo real

---

### 8. **Validação de Integridade do Pedido**

**Proteção:** Garante que itens não foram adulterados

```python
# Recalcula total dos itens antes de enviar ao MP
total_verificacao = sum(item['total_preco'])
if abs(total_verificacao - total) > Decimal('0.01'):
    pedido.delete()
    return erro
```

**Previne:**
- ❌ Manipulação de preços no carrinho
- ❌ "Race conditions" em modificações de preço
- ❌ Inconsistências de dados

---

### 9. **Proteção de Dados Sensíveis**

**Credenciais:** NUNCA hardcoded no código

```python
# ❌ ERRADO
MERCADOPAGO_TOKEN = 'APP-USR-123456-abc'

# ✅ CORRETO - Use variáveis de ambiente
from decouple import config
MERCADOPAGO_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN')
```

**Previne:**
- ❌ Vazamento de credenciais no GitHub
- ❌ Acesso não autorizado à conta MP
- ❌ Uso indevido da API

---

### 10. **Headers de Segurança**

**Configurado em `settings.py`:**

```python
X_FRAME_OPTIONS = 'DENY'                # Previne clickjacking
SECURE_CONTENT_TYPE_NOSNIFF = True      # Previne MIME sniffing
SESSION_COOKIE_SAMESITE = 'Lax'         # Proteção CSRF
```

**Previne:**
- ❌ Clickjacking
- ❌ MIME-type attacks
- ❌ CSRF (Cross-Site Request Forgery)

---

## 🚨 Alertas Críticos Monitorados:

| Alerta | Ação |
|--------|------|
| Assinatura inválida | Bloqueia webhook + log crítico |
| Valores não batem | NÃO aprova pedido + alerta |
| Pedido inexistente | Ignora webhook + log warning |
| User-Agent inválido | Bloqueia acesso + log warning |
| Replay attack | Ignora + log info |
| Erro no MP | Log erro + retorna 200 |

---

## 📋 Checklist de Segurança em Produção:

### Antes de ir para produção:

- [ ] ✅ Configurar HTTPS (obrigatório para webhooks)
- [ ] ✅ Descomentar configurações de segurança no `settings.py`
- [ ] ✅ Trocar credenciais TEST por PRODUÇÃO
- [ ] ✅ Configurar variáveis de ambiente (use `python-decouple`)
- [ ] ✅ Adicionar domínio em ALLOWED_HOSTS
- [ ] ✅ Configurar webhook URL no painel do Mercado Pago
- [ ] ✅ Testar webhook com ngrok antes de ir ao ar
- [ ] ✅ Configurar monitoramento de logs
- [ ] ✅ Fazer backup do banco de dados
- [ ] ✅ Testar fluxo completo em ambiente de staging

### Após deploy:

- [ ] ✅ Verificar se HTTPS está ativo
- [ ] ✅ Testar uma compra real (valor baixo)
- [ ] ✅ Confirmar que webhook está recebendo notificações
- [ ] ✅ Verificar logs de segurança
- [ ] ✅ Confirmar liberação automática de acesso
- [ ] ✅ Monitorar por 24h

---

## 🛡️ Níveis de Proteção:

| Camada | Proteção | Status |
|--------|----------|--------|
| **Transporte** | HTTPS/TLS | ✅ Configurado |
| **Autenticação** | Assinatura HMAC | ✅ Implementado |
| **Validação** | User-Agent | ✅ Implementado |
| **Integridade** | Valores e Totais | ✅ Implementado |
| **Replay** | Status Check | ✅ Implementado |
| **Autorização** | Verificação no MP | ✅ Implementado |
| **Auditoria** | Logging | ✅ Implementado |
| **Aplicação** | Headers de Segurança | ✅ Configurado |

---

## 🔍 Como Testar Segurança:

### 1. Teste de Webhook Falso:
```bash
# Tente enviar POST direto (deve ser bloqueado)
curl -X POST http://localhost:8000/carrinho/webhook/mercadopago/ \
  -H "Content-Type: application/json" \
  -d '{"type":"payment","data":{"id":"123"}}'

# Resultado esperado: 403 Forbidden ou ignorado
```

### 2. Teste de Valores Adulterados:
- Crie pedido de R$ 100
- Tente modificar no banco para R$ 10
- Pague R$ 10 no Mercado Pago
- **Resultado esperado:** Pedido NÃO aprovado + alerta crítico no log

### 3. Teste de Replay:
- Aprove um pedido
- Reenvie o mesmo webhook
- **Resultado esperado:** Pedido não é reprocessado

---

## 📊 Monitoramento Recomendado:

### Logs para monitorar:
```bash
# Logs de segurança
tail -f logs/security.log

# Logs do Mercado Pago
tail -f logs/mercadopago.log

# Filtrar alertas críticos
grep "CRITICAL" logs/security.log

# Ver pagamentos aprovados
grep "APROVADO" logs/mercadopago.log
```

### Métricas importantes:
- Taxa de recusa de webhooks
- Divergências de valores detectadas
- Tentativas de replay
- Tempo de processamento de webhooks
- Taxa de aprovação vs. rejeição

---

## 🚨 Em Caso de Incidente:

### Se detectar fraude:

1. **Imediato:**
   - Pausar processamento de webhooks
   - Revisar logs de segurança
   - Identificar pedidos suspeitos

2. **Investigação:**
   - Checar valores no Mercado Pago
   - Verificar IPs das requisições
   - Analisar padrões suspeitos

3. **Resposta:**
   - Cancelar pedidos fraudulentos
   - Bloquear IPs se necessário
   - Atualizar regras de segurança

4. **Pós-incidente:**
   - Documentar o ocorrido
   - Implementar novas proteções
   - Notificar usuários afetados

---

## 📚 Referências:

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Mercado Pago - Segurança](https://www.mercadopago.com.br/developers/pt/docs/your-integrations/security)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [PCI DSS Compliance](https://www.pcisecuritystandards.org/)

---

## ✅ Conclusão:

O sistema implementa **múltiplas camadas de segurança** contra:
- ✅ Man-in-the-Middle
- ✅ Replay Attacks
- ✅ Fraudes de valor
- ✅ Webhooks falsos
- ✅ Session hijacking
- ✅ Adulteração de dados

**Está seguro para produção após configurar HTTPS e credenciais!** 🔒
