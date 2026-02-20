# ⚠️ ALTERAÇÕES PARA MODO DE DESENVOLVIMENTO

## 📝 Resumo das Mudanças

Este arquivo documenta as alterações feitas para permitir testes locais sem as validações de segurança do webhook do Mercado Pago.

---

## 🔓 Validações de Segurança Desabilitadas

### Arquivo: `carrinho/views.py` - Função `mp_webhook()`

As seguintes validações foram **COMENTADAS** (linhas mantidas no código, apenas com `#` na frente):

1. **Validação de User-Agent**
   - Verificava se a requisição vinha realmente do Mercado Pago
   - Linha: ~290

2. **Validação de Assinatura HMAC (x-signature)**
   - Validava a assinatura criptográfica do webhook
   - Prevenia ataques Man-in-the-Middle
   - Linhas: ~295-325

3. **Validação de Valor do Pagamento**
   - Verificava se o valor pago batia com o total do pedido
   - Proteção anti-fraude crítica
   - Linhas: ~360-370

4. **Validação de Replay Attack**
   - Impedia processar o mesmo pagamento duas vezes
   - Linhas: ~372-376

5. **Validação Estrita da API do MP**
   - Agora continua mesmo se não encontrar o pagamento na API
   - Cria um objeto de pagamento fake para testes
   - Linhas: ~335-350

---

## ✅ O Que Foi Adicionado

### 1. Comando: `simular_pagamento`

**Arquivo:** `carrinho/management/commands/simular_pagamento.py`

**Uso:**
```bash
# Aprovar um pedido
python manage.py simular_pagamento 1

# Rejeitar um pedido
python manage.py simular_pagamento 1 --status=rejected

# Deixar pendente
python manage.py simular_pagamento 1 --status=pending
```

**Funcionalidade:**
- Simula uma chamada do webhook do Mercado Pago
- Funciona 100% offline
- Permite testar todos os cenários de pagamento
- Atualiza o status do pedido e libera acessos

---

### 2. Comando: `listar_pedidos`

**Arquivo:** `carrinho/management/commands/listar_pedidos.py`

**Uso:**
```bash
# Listar últimos 10 pedidos
python manage.py listar_pedidos

# Listar todos os pedidos
python manage.py listar_pedidos --ultimos=0

# Filtrar por status
python manage.py listar_pedidos --status=aprovado

# Filtrar por usuário
python manage.py listar_pedidos --usuario=user@example.com
```

**Funcionalidade:**
- Lista todos os pedidos com formatação colorida
- Mostra itens, status, valores, acessos liberados
- Exibe estatísticas e resumos
- Facilita acompanhamento dos testes

---

### 3. Documentação de Testes

**Arquivo:** `TESTES_DEV.md`

Guia completo de como testar o sistema em desenvolvimento, incluindo:
- Como usar os comandos de simulação
- Como testar com credenciais do Mercado Pago
- Como configurar ngrok para webhook real
- Cenários de teste completos
- Troubleshooting

---

## 🔒 Como Reativar a Segurança (PRODUÇÃO)

### ⚠️ CRÍTICO: Antes de colocar em produção!

1. **Abra:** `carrinho/views.py`
2. **Localize a função:** `mp_webhook()`
3. **Descomente todas as linhas** que começam com `# #`

**Exemplo:**

De:
```python
# # 1. VALIDAÇÃO: Verificar se vem do Mercado Pago (User-Agent)
# user_agent = request.META.get('HTTP_USER_AGENT', '')
# if 'MercadoPago' not in user_agent:
#     security_logger.warning(...)
#     return HttpResponseForbidden('Invalid User-Agent')
```

Para:
```python
# 1. VALIDAÇÃO: Verificar se vem do Mercado Pago (User-Agent)
user_agent = request.META.get('HTTP_USER_AGENT', '')
if 'MercadoPago' not in user_agent:
    security_logger.warning(...)
    return HttpResponseForbidden('Invalid User-Agent')
```

4. **Faça o mesmo** para todas as outras validações comentadas

5. **Ative HTTPS** em `personal/settings.py`:
```python
DEBUG = False
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

6. **Configure o webhook real** no painel do Mercado Pago

7. **Use credenciais de PRODUÇÃO** (não de teste)

---

## 📋 Checklist para Produção

- [ ] Descomentar todas as validações de segurança em `mp_webhook()`
- [ ] Alterar `DEBUG = False` em `settings.py`
- [ ] Ativar todas as configurações de HTTPS
- [ ] Usar credenciais de PRODUÇÃO do Mercado Pago
- [ ] Configurar webhook com URL HTTPS real (não localhost)
- [ ] Testar em ambiente de homologação primeiro
- [ ] Verificar logs de segurança
- [ ] Fazer backup do banco de dados

---

## 🎯 Fluxo de Desenvolvimento vs Produção

| Aspecto | Desenvolvimento (Atual) | Produção (Necessário) |
|---------|------------------------|----------------------|
| User-Agent | ❌ Desabilitado | ✅ Validar MP |
| Assinatura HMAC | ❌ Desabilitada | ✅ Obrigatória |
| Validação de Valor | ❌ Desabilitada | ✅ Crítica |
| Replay Attack | ❌ Desabilitado | ✅ Prevenir |
| API do MP | ⚠️ Continua sem | ✅ Obrigatória |
| Webhook | 🔧 Simular comando | ✅ Real via HTTPS |
| Credenciais | 🧪 TEST ou fake | ✅ PRODUÇÃO |
| HTTPS | ❌ HTTP ok | ✅ Obrigatório |
| Logs | ℹ️ Info | ⚠️ Warning/Error |

---

## 🆘 Em Caso de Dúvida

1. **Para desenvolvimento:** Leia `TESTES_DEV.md`
2. **Para segurança:** Leia `SEGURANCA.md`
3. **Para Mercado Pago:** Leia `MERCADOPAGO_README.md`
4. **Para restaurar segurança:** Siga este arquivo (seção "Como Reativar")

---

## ⏱️ Data das Alterações

**Data:** 19 de fevereiro de 2026
**Motivo:** Permitir testes locais sem configurar ngrok/webhook real
**Removido em produção:** NÃO - Manter comentários para referência
**Status:** ⚠️ TEMPORÁRIO - Reativar antes de produção!

---

**⚠️ LEMBRETE IMPORTANTE:**

> Este é um modo de desenvolvimento. **NUNCA coloque em produção sem reativar todas as validações de segurança!** O sistema está vulnerável a ataques Man-in-the-Middle, fraudes e replay attacks enquanto as validações estiverem desabilitadas.
