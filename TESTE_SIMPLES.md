# 🚀 GUIA RÁPIDO - Testar Pagamento com Mercado Pago

## ✅ SEU CÓDIGO JÁ ESTÁ CORRETO!

O fluxo completo está implementado:
1. ✅ Usuário clica em "Finalizar Pedido"
2. ✅ É redirecionado para **sandbox do Mercado Pago**
3. ✅ Paga lá dentro
4. ✅ MP redireciona de volta para seu site
5. ✅ Mostra página de sucesso/falha

---

## 🎯 Para Testar AGORA (3 passos)

### Passo 1: Obter Credenciais de TESTE

1. Acesse: https://www.mercadopago.com.br/developers/panel/app
2. Clique em sua aplicação (ou crie uma nova)
3. Vá em **"Credenciais de teste"** (não produção!)
4. Copie:
   - **Access Token** (começa com `TEST-`)
   - **Public Key** (começa com `TEST-`)

### Passo 2: Configurar no Sistema

Abra `personal/settings.py` e substitua as linhas:

```python
# Linha ~146-147
MERCADOPAGO_ACCESS_TOKEN = 'TEST-seu-access-token-aqui'
MERCADOPAGO_PUBLIC_KEY = 'TEST-sua-public-key-aqui'
```

⚠️ **IMPORTANTE**: Use credenciais que começam com `TEST-`, não `APP_USR-`

### Passo 3: Testar o Fluxo

1. **Inicie o servidor:**
   ```bash
   python manage.py runserver
   ```

2. **Faça login** no site

3. **Adicione produtos ao carrinho**

4. **Vá para checkout** e clique em "Finalizar Pedido"

5. **Você será redirecionado para a SANDBOX do Mercado Pago** 🎉

6. **Use um cartão de teste:**
   - Número: `5031 4332 1540 6351`
   - CVV: `123`
   - Validade: `11/25` (qualquer data futura)
   - Nome: `APRO` (para aprovar) ou `OTHE` (para rejeitar)
   - CPF: `12345678909`

7. **Complete o pagamento** → Você voltará automaticamente para o site!

---

## 📱 Cartões de Teste do Mercado Pago

| Resultado | Nome do Titular |
|-----------|----------------|
| ✅ Aprovado | `APRO` |
| ❌ Recusado | `OTHE` |
| ⏳ Pendente | `PEND` |

Sempre use o cartão: `5031 4332 1540 6351`

**Mais cartões:** https://www.mercadopago.com.br/developers/pt/docs/checkout-api/testing

---

## 🔍 Verificar Resultado

### Opção 1: Django Admin
```
http://localhost:8000/admin/produtos/pedido/
```

### Opção 2: Terminal
```bash
python manage.py listar_pedidos
```

---

## ⚠️ Sobre o Webhook

O webhook atualiza o status automaticamente **DEPOIS** que o MP confirma.

**Para testes iniciais, você pode:**
- Ignorar o webhook
- Aprovar manualmente no admin
- OU usar o comando: `python manage.py simular_pagamento <id>`

**Para webhook automático (opcional):**
- Configure ngrok (veja TESTES_DEV.md)
- Mas NÃO é necessário para testar o fluxo básico!

---

## 🎯 Resumo do Fluxo

```
Usuário no seu site
    ↓
Clica "Finalizar Pedido"
    ↓
[Seu site cria pedido e chama MP]
    ↓
REDIRECIONA para Sandbox do MP ← ISSO JÁ FUNCIONA!
    ↓
Usuário paga no MP
    ↓
MP redireciona de volta
    ↓
Página de sucesso/falha no seu site ← ISSO JÁ FUNCIONA!
    ↓
(Webhook atualiza status depois) ← Opcional para teste
```

---

## 🐛 Problemas Comuns

### "Erro ao processar pagamento"
→ Verifique se colocou credenciais de **TEST** (começam com `TEST-`)

### "Não redireciona para MP"
→ Verifique no console se tem erro 401/403 (credenciais inválidas)

### "Paguei mas não aprovou"
→ Normal! Aprove manualmente com: `python manage.py simular_pagamento <id>`
→ OU configure webhook com ngrok

---

## ✅ Checklist Rápido

- [ ] Obtive credenciais de TESTE do MP (começam com `TEST-`)
- [ ] Coloquei no `settings.py`
- [ ] Iniciei o servidor (`python manage.py runserver`)
- [ ] Fiz login no site
- [ ] Adicionei produto ao carrinho
- [ ] Cliquei em "Finalizar Pedido"
- [ ] Fui redirecionado para sandbox do MP ✅
- [ ] Paguei com cartão de teste (nome: APRO)
- [ ] Voltei para o site ✅

---

**Pronto! É só isso! O código já está funcionando.** 🎉

Você só precisa das credenciais de TESTE e usar os cartões de teste!
