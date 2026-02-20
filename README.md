# Sistema de Pagamento com Mercado Pago - Personal Trainer

Sistema completo de e-commerce para venda de produtos digitais (treinos, consultorias) com integração ao Mercado Pago Checkout Pro.

## 🚀 Funcionalidades

- ✅ Catálogo de produtos
- ✅ Carrinho de compras
- ✅ Checkout integrado com Mercado Pago
- ✅ Webhook para confirmação automática de pagamentos
- ✅ Dashboard do cliente com produtos adquiridos
- ✅ Sistema de contas de usuário
- ✅ Área administrativa Django

## 📋 Configuração Inicial

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPO.git
cd SEU_REPO
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar credenciais

Edite `personal/settings.py` e configure:

```python
# SECRET_KEY - Gere uma nova em https://djecrety.ir/
SECRET_KEY = 'sua-secret-key-aqui'

# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN = 'seu-access-token'
MERCADOPAGO_PUBLIC_KEY = 'sua-public-key'
```

### 5. Executar migrações

```bash
python manage.py migrate
```

### 6. Criar superusuário

```bash
python manage.py createsuperuser
```

### 7. Rodar servidor

```bash
python manage.py runserver
```

## 🔧 Configuração do Mercado Pago

### Ambiente de Teste

1. Acesse: https://www.mercadopago.com.br/developers/panel/app
2. Vá em **Credenciais de teste**
3. Copie `Access Token` e `Public Key`
4. Configure em `settings.py`:
   ```python
   MERCADOPAGO_MODE = 'test'
   MERCADOPAGO_TEST_ONLY = True
   ```

### Ambiente de Produção

Consulte [CHECKLIST_PRODUCAO_MP.md](CHECKLIST_PRODUCAO_MP.md) para o passo a passo completo.

## 📁 Estrutura do Projeto

```
personal/
├── accounts/         # Sistema de usuários
├── produtos/         # Catálogo e produtos digitais
├── carrinho/         # Carrinho de compras
├── checkout/         # Processamento de pagamentos
├── dashboard/        # Área do cliente
├── agendamento/      # Sistema de agendamentos
├── personal/         # Configurações do projeto
└── templates/        # Templates HTML
```

## 🔒 Segurança

- Nunca commite credenciais reais
- Use HTTPS em produção
- Ative todas as validações do webhook em produção
- Configure ALLOWED_HOSTS corretamente

## 📝 Licença

Projeto privado - Todos os direitos reservados

## 🤝 Suporte

Para dúvidas sobre integração do Mercado Pago:
- Documentação: https://www.mercadopago.com.br/developers/pt/docs/checkout-pro
- Painel: https://www.mercadopago.com.br/developers/panel/app
