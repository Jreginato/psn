# 🧪 GUIA DE TESTES EM DESENVOLVIMENTO

## ⚠️ MODO ATUAL: DESENVOLVIMENTO (Validações de Segurança Desabilitadas)

O sistema está configurado para testes locais. **Todas as validações de segurança do webhook foram comentadas** para facilitar os testes.

---

## 🎯 Como Testar o Fluxo Completo

### 1. **Teste Básico (Sem Mercado Pago Real)**

Você pode testar todo o fluxo de checkout sem precisar de credenciais do Mercado Pago:

#### Passo a passo:

1. **Adicione produtos ao carrinho** e vá até o checkout
2. **Crie um pedido** (será redirecionado mas pode dar erro - normal)
3. **Anote o ID do pedido** que aparecerá na URL ou no Django Admin
4. **Simule a aprovação do pagamento** com o comando:

```bash
python manage.py simular_pagamento <ID_DO_PEDIDO>
```

**Exemplos:**
```bash
# Aprovar pedido #5
python manage.py simular_pagamento 5

# Rejeitar pedido #5
python manage.py simular_pagamento 5 --status=rejected

# Deixar pedido #5 pendente
python manage.py simular_pagamento 5 --status=pending
```

---

### 2. **Teste com Mercado Pago Real (Recomendado)**

Para testar com o fluxo completo do Mercado Pago:

#### a) Configure as credenciais de TESTE:

1. Acesse: https://www.mercadopago.com.br/developers
2. Vá em **"Suas aplicações"** → **"Criar aplicação"**
3. Copie o **Access Token** e **Public Key** de **TESTE**
4. Cole em `personal/settings.py`:

```python
MERCADOPAGO_ACCESS_TOKEN = 'TEST-seu-token-aqui'
MERCADOPAGO_PUBLIC_KEY = 'TEST-sua-chave-aqui'
```

#### b) Teste com cartões de teste:

1. **Adicione produtos ao carrinho**
2. **Finalize a compra** → será redirecionado para o Mercado Pago
3. **Use um cartão de teste:**

**Para aprovar:**
- Cartão: `5031 4332 1540 6351`
- CVV: Qualquer 3 dígitos
- Validade: Qualquer data futura
- Titular: APRO (importante!)
- CPF: Qualquer

**Para rejeitar:**
- Cartão: `5031 4332 1540 6351`
- Titular: OTHE
- Resto igual

4. **Após pagar**, você será redirecionado de volta ao site
5. **Aprove manualmente** no Django Admin ou com o comando:

```bash
python manage.py simular_pagamento <ID_DO_PEDIDO>
```

**Mais cartões de teste:** https://www.mercadopago.com.br/developers/pt/docs/checkout-api/testing

---

### 3. **Teste com Webhook Real (Avançado)**

Para que o webhook funcione automaticamente após o pagamento, você precisa expor o localhost:

#### Opção A: Usando ngrok (Recomendado)

1. **Instale o ngrok:** https://ngrok.com/download
2. **Execute:**
   ```bash
   ngrok http 8000
   ```
3. **Copie a URL** gerada (ex: `https://abc123.ngrok.io`)
4. **Configure no Mercado Pago:**
   - Vá em: https://www.mercadopago.com.br/developers → Sua aplicação → Webhooks
   - Cole a URL: `https://abc123.ngrok.io/webhook/mercadopago/`
5. **Teste o fluxo completo** - agora o pedido será aprovado automaticamente!

#### Opção B: Usando localtunnel

```bash
npm install -g localtunnel
lt --port 8000
```

---

## 📋 Verificar Pedidos Criados

### No Django Admin:
```
http://localhost:8000/admin/produtos/pedido/
```

### Via Terminal:
```bash
python manage.py shell
```

Depois execute:
```python
from produtos.models import Pedido

# Listar todos os pedidos
for p in Pedido.objects.all():
    print(f"#{p.id}: {p.status} - R$ {p.total} - {p.usuario.email}")

# Ver detalhes de um pedido específico
pedido = Pedido.objects.get(id=1)
print(f"Status: {pedido.status}")
print(f"Total: R$ {pedido.total}")
print(f"Aprovado em: {pedido.aprovado_em}")
print(f"Itens:")
for item in pedido.itens.all():
    print(f"  - {item.nome_produto}: R$ {item.preco_unitario}")
```

---

## 🔍 Ver Logs

Os logs estão sendo salvos em:
- `logs/mercadopago.log` - Logs do processamento de pagamento
- `logs/security.log` - Logs de segurança (quando reativados)

```bash
# Ver últimos logs
tail -n 50 logs/mercadopago.log

# Seguir logs em tempo real
tail -f logs/mercadopago.log
```

**No Windows:**
```powershell
Get-Content logs\mercadopago.log -Tail 50
Get-Content logs\mercadopago.log -Wait
```

---

## 🔒 Ativar Segurança para Produção

**IMPORTANTE:** Antes de colocar em produção, você DEVE reativar todas as validações de segurança!

### Arquivo: `carrinho/views.py`

Descomente todas as seções que começam com:
```python
# # 1. VALIDAÇÃO: Verificar se vem do Mercado Pago (User-Agent)
# # 2. VALIDAÇÃO: Verificar assinatura x-signature
# # 6. VALIDAÇÃO CRÍTICA: Verificar se o valor pago bate
# # 7. VALIDAÇÃO: Verificar se o pedido não foi aprovado anteriormente
```

Basta remover os `# ` do início de cada linha (descomemtar).

### Arquivo: `personal/settings.py`

Descomente e ative:
```python
# Debug deve estar False em produção
DEBUG = False

# HTTPS obrigatório
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## 🎪 Cenários de Teste

### Teste 1: Fluxo completo de aprovação
1. Adicionar produtos ao carrinho
2. Ir para checkout
3. Criar pedido
4. Simular aprovação: `python manage.py simular_pagamento <id>`
5. Verificar que o status mudou para "aprovado"
6. Verificar que o acesso aos produtos foi liberado

### Teste 2: Pagamento rejeitado
1. Criar pedido
2. Simular rejeição: `python manage.py simular_pagamento <id> --status=rejected`
3. Verificar que o status mudou para "cancelado"
4. Verificar que o acesso NÃO foi liberado

### Teste 3: Pagamento pendente
1. Criar pedido
2. Simular pendência: `python manage.py simular_pagamento <id> --status=pending`
3. Verificar que o status mudou para "processando"
4. Aprovar depois: `python manage.py simular_pagamento <id>`

### Teste 4: Com Mercado Pago real
1. Configurar credenciais de TESTE
2. Fazer pedido real
3. Pagar com cartão de teste (APRO)
4. Aprovar manualmente com o comando
5. Verificar acesso liberado

### Teste 5: Webhook automático (com ngrok)
1. Configurar ngrok
2. Adicionar webhook no Mercado Pago
3. Fazer pedido
4. Pagar com cartão de teste
5. Verificar que aprovou automaticamente (sem comando manual)

---

## 💡 Dicas

- **Sempre teste primeiro SEM credenciais do MP** usando o comando `simular_pagamento`
- **Use credenciais de TESTE** do Mercado Pago, nunca as de produção!
- **O comando `simular_pagamento` funciona offline** e é perfeito para desenvolvimento
- **Para produção**, lembre-se de reativar todas as validações de segurança!
- **Os cartões de teste do MP** simulam diferentes cenários (aprovado, rejeitado, etc)

---

## 🐛 Problemas Comuns

### "Pedido não encontrado"
- Verifique o ID correto no admin: http://localhost:8000/admin/produtos/pedido/

### "Erro ao conectar com Mercado Pago"
- Verifique se o `MERCADOPAGO_ACCESS_TOKEN` está correto em `settings.py`
- Use as credenciais de **TESTE**, não de produção
- Em modo dev, o erro será ignorado e você pode usar `simular_pagamento`

### "Webhook não é chamado automaticamente"
- Normal! Em localhost o Mercado Pago não consegue chamar seu webhook
- Use o comando `simular_pagamento` OU configure ngrok/localtunnel

### "Pedido não aprova após simular"
- Verifique os logs: `logs/mercadopago.log`
- Execute o comando com mais detalhes

---

## 📚 Próximos Passos

1. ✅ **Testar localmente** com `simular_pagamento`
2. ✅ **Obter credenciais de TESTE** do Mercado Pago
3. ✅ **Testar com cartões de teste**
4. ⚠️ **Configurar ngrok** para webhook automático (opcional)
5. ⚠️ **Reativar validações de segurança** antes de produção
6. ⚠️ **Usar credenciais de PRODUÇÃO** apenas em servidor real
7. ⚠️ **Configurar HTTPS** em produção
8. ⚠️ **Configurar webhook real** no painel do Mercado Pago

---

**Precisa de ajuda? Leia:** `SEGURANCA.md` e `MERCADOPAGO_README.md`
