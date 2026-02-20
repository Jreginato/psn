# 💳 Mercado Pago - Configuração

## ✅ O que foi implementado:

### 1. **Integração Completa**
- ✅ SDK do Mercado Pago instalado
- ✅ Criação de preferência de pagamento
- ✅ Redirecionamento para checkout do MP
- ✅ Webhook para processar pagamentos
- ✅ Liberação automática de produtos após aprovação
- ✅ Páginas de retorno (sucesso, falha, pendente)

### 2. **Fluxo Completo:**
1. Cliente adiciona produtos ao carrinho
2. Clica em "Finalizar Compra"
3. **Pedido é criado** no banco com status "pendente"
4. **Redireciona para Mercado Pago** para pagamento
5. Cliente paga (PIX, cartão, boleto, etc)
6. **Mercado Pago notifica via webhook**
7. Sistema **aprova pedido** e **libera acesso**
8. Cliente acessa produtos na **Área do Aluno**

---

## 🚀 Como Configurar:

### 1. **Obter Credenciais do Mercado Pago**

#### Criar conta (se não tiver):
- Acesse: https://www.mercadopago.com.br/
- Cadastre-se gratuitamente

#### Obter Access Token e Public Key:
1. Entre em: https://www.mercadopago.com.br/developers
2. Vá em **"Suas integrações"** > **"Criar aplicação"**
3. Escolha **"Pagamentos online"**
4. Copie as credenciais:
   - **Access Token** (começa com `TEST-` ou `APP-USR-`)
   - **Public Key** (começa com `TEST-` ou `APP-USR-`)

---

### 2. **Configurar no Django**

Edite o arquivo `personal/settings.py`:

```python
# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN = 'SEU_ACCESS_TOKEN_AQUI'
MERCADOPAGO_PUBLIC_KEY = 'SUA_PUBLIC_KEY_AQUI'
```

**⚠️ IMPORTANTE:**
- Use credenciais de **TESTE** primeiro
- Depois migre para **PRODUÇÃO**
- **NUNCA** commite as credenciais no GitHub

---

### 3. **Testar no Modo Sandbox**

#### Credenciais de Teste:
Para testar, use as credenciais que começam com `TEST-`

#### Cartões de Teste:
Use estes cartões para simular pagamentos:

**Aprovado:**
- Número: `5031 4332 1540 6351`
- CVV: `123`
- Validade: Qualquer data futura
- Nome: Qualquer nome

**Recusado:**
- Número: `5031 7557 3453 0604`
- CVV: `123`
- Validade: Qualquer data futura

**Pendente:**
- Use PIX ou boleto no teste

Mais cartões: https://www.mercadopago.com.br/developers/pt/docs/testing/test-cards

---

### 4. **Configurar Webhook em Produção**

Quando for para produção, configure o webhook no Mercado Pago:

1. Acesse: https://www.mercadopago.com.br/developers
2. Vá em sua aplicação
3. Configure a URL de notificação:
   ```
   https://seudominio.com/carrinho/webhook/mercadopago/
   ```
4. Marque o evento: **"Pagamentos"**

**⚠️ IMPORTANTE:**
- O webhook precisa de **HTTPS** (não funciona em localhost)
- Para testar localmente, use **ngrok** ou **Localtunnel**

---

### 5. **Testar Webhook Localmente (Opcional)**

#### Usando ngrok:
```bash
# Instalar ngrok
# https://ngrok.com/download

# Executar
ngrok http 8000

# Copie a URL gerada (ex: https://abc123.ngrok.io)
# Configure no Mercado Pago:
# https://abc123.ngrok.io/carrinho/webhook/mercadopago/
```

#### Usando Localtunnel:
```bash
# Instalar
npm install -g localtunnel

# Executar
lt --port 8000

# Configure a URL gerada no MP
```

---

## 🔐 Segurança - Variáveis de Ambiente

**NÃO** deixe as credenciais hardcoded no código!

### Usar python-decouple:

```bash
pip install python-decouple
```

Crie arquivo `.env` na raiz:
```
MERCADOPAGO_ACCESS_TOKEN=SEU_TOKEN_AQUI
MERCADOPAGO_PUBLIC_KEY=SUA_KEY_AQUI
```

Atualize `settings.py`:
```python
from decouple import config

MERCADOPAGO_ACCESS_TOKEN = config('MERCADOPAGO_ACCESS_TOKEN')
MERCADOPAGO_PUBLIC_KEY = config('MERCADOPAGO_PUBLIC_KEY')
```

Adicione `.env` no `.gitignore`:
```
.env
```

---

## 📊 Status dos Pedidos:

| Status | Descrição |
|--------|-----------|
| **pendente** | Pedido criado, aguardando pagamento |
| **processando** | Pagamento em análise (boleto, PIX pendente) |
| **aprovado** | Pagamento aprovado, acesso liberado |
| **cancelado** | Pagamento recusado ou cancelado |
| **reembolsado** | Pedido reembolsado |

---

## 🛠️ Solução de Problemas:

### Erro: "Invalid access token"
- Verifique se o Access Token está correto
- Certifique-se de usar o token completo (começa com TEST- ou APP-USR-)

### Webhook não recebe notificações:
- Webhook precisa de HTTPS em produção
- Use ngrok para testar localmente
- Verifique se a URL está correta no painel do MP
- Certifique-se que a rota não exige CSRF (já está com @csrf_exempt)

### Pagamento aprovado mas acesso não liberado:
- Verifique se o webhook está funcionando
- Veja os logs no terminal quando receber notificação
- Confirme que `pedido.liberar_acesso_produtos()` está sendo chamado

### Erro ao criar preferência:
- Verifique se o total do pedido é maior que 0
- Confirme que os itens têm preço válido
- Veja se as URLs de retorno estão corretas

---

## 🎯 Próximos Passos (Opcional):

1. **Email de Confirmação:**
   - Enviar email quando pedido for aprovado
   - Usar Django email backend

2. **Notificações Push:**
   - Notificar cliente via PWA quando pago

3. **Assinatura Recorrente:**
   - Implementar para consultoria mensal
   - Usar Mercado Pago Subscriptions

4. **Desconto/Cupons:**
   - Sistema de cupons de desconto
   - Aplicar no checkout

---

## 📚 Recursos:

- [Documentação MP](https://www.mercadopago.com.br/developers/pt/docs)
- [SDK Python](https://github.com/mercadopago/sdk-python)
- [Cartões de Teste](https://www.mercadopago.com.br/developers/pt/docs/testing/test-cards)
- [Webhooks](https://www.mercadopago.com.br/developers/pt/docs/your-integrations/notifications/webhooks)

---

## ✨ Pronto!

Teste agora:
1. Adicione produtos ao carrinho
2. Finalize a compra
3. Use um cartão de teste
4. Confirme que o acesso foi liberado!

🚀 Sua loja está pronta para vender!
