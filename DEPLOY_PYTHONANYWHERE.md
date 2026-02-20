# 🚀 Guia de Deploy no PythonAnywhere

## 📋 Pré-requisitos

1. Conta no PythonAnywhere (https://www.pythonanywhere.com)
2. Credenciais de produção do Mercado Pago
3. Código no GitHub (recomendado)

---

## 🔧 Passo 1: Configurar Ambiente Local

### 1.1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 1.2. Configurar variáveis de ambiente locais
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env com suas credenciais de TESTE
# Configure DJANGO_ENV=development
```

### 1.3. Testar localmente
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## ☁️ Passo 2: Preparar PythonAnywhere

### 2.1. Criar conta
1. Acesse https://www.pythonanywhere.com
2. Crie uma conta gratuita (ou paga)
3. Acesse o Dashboard

### 2.2. Criar Web App
1. Vá em **"Web"** no menu superior
2. Clique em **"Add a new web app"**
3. Escolha **"Manual configuration"**
4. Selecione **Python 3.10** (ou versão disponível)

---

## 📦 Passo 3: Upload do Código

### Opção A: Via Git (Recomendado)

No **Bash Console** do PythonAnywhere:

```bash
# Clonar repositório
cd ~
git clone https://github.com/seu-usuario/seu-repo.git personal

# Entrar na pasta
cd personal
```

### Opção B: Via Upload Manual

1. Use o **Files** do PythonAnywhere
2. Faça upload dos arquivos
3. Ou use o **"Upload a file"**

---

## 🐍 Passo 4: Configurar Virtualenv

No **Bash Console** do PythonAnywhere:

```bash
# Criar virtualenv
cd ~
python3.10 -m venv personal-venv

# Ativar virtualenv
source personal-venv/bin/activate

# Instalar dependências
cd ~/personal
pip install -r requirements.txt
```

---

## 🗄️ Passo 5: Configurar Variáveis de Ambiente e Banco de Dados

### 5.1. Configurar variáveis de ambiente

No **Bash Console**:

```bash
cd ~/personal

# Criar arquivo .env para PRODUÇÃO
nano .env
```

Cole o seguinte conteúdo (ajuste com suas credenciais):

```bash
# ===== PRODUÇÃO =====
DJANGO_ENV=production

# Django
SECRET_KEY=sua-secret-key-super-segura-unica-gerada-em-djecrety
ALLOWED_HOST=seuusuario.pythonanywhere.com

# Mercado Pago - PRODUÇÃO
MP_ACCESS_TOKEN_PROD=APP-USR-seu-token-real-de-producao
MP_PUBLIC_KEY_PROD=APP-USR-sua-public-key-de-producao
```

Salve com `Ctrl+O`, `Enter`, `Ctrl+X`

**Nota:** O sistema usa SQLite (db.sqlite3) que será criado automaticamente na migração.

### 5.2. Migrar banco de dados

```bash
source ~/personal-venv/bin/activate
cd ~/personal
python manage.py migrate
python manage.py createsuperuser
```

---

## 🌐 Passo 6: Configurar WSGI

1. Vá em **"Web"** > sua aplicação
2. Clique no link do arquivo **WSGI configuration file**
3. **Apague todo o conteúdo** e cole:

```python
import os
import sys
from pathlib import Path

# Adicionar diretórios ao path
path = '/home/seuusuario/personal'  # MUDE 'seuusuario' pelo seu username
if path not in sys.path:
    sys.path.insert(0, path)

# Configurar variável de ambiente do Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'personal.settings'

# Definir variáveis de ambiente (ou use um arquivo .env carregado pelo sistema)
# Opção 1: Definir diretamente aqui (CUIDADO: não commite credenciais!)
os.environ.setdefault('DJANGO_ENV', 'production')
os.environ.setdefault('SECRET_KEY', 'sua-secret-key-super-segura')
os.environ.setdefault('ALLOWED_HOST', 'seuusuario.pythonanywhere.com')
os.environ.setdefault('MP_ACCESS_TOKEN_PROD', 'APP-USR-seu-token-real')
os.environ.setdefault('MP_PUBLIC_KEY_PROD', 'APP-USR-sua-key-real')

# Opção 2: Carregar de arquivo .env manualmente
# with open('/home/seuusuario/personal/.env') as f:
#     for line in f:
#         if line.strip() and not line.startswith('#'):
#             key, value = line.strip().split('=', 1)
#             os.environ.setdefault(key, value)

# Inicializar aplicação Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**IMPORTANTE**: Troque `seuusuario` pelo seu username do PythonAnywhere!

---

## 📁 Passo 7: Configurar Arquivos Estáticos

### 7.1. Coletar arquivos estáticos

No **Bash Console**:

```bash
source ~/personal-venv/bin/activate
cd ~/personal
python manage.py collectstatic --noinput
```

### 7.2. Configurar no Web App

1. Vá em **"Web"** > sua aplicação
2. Role até **"Static files"**
3. Adicione:
   - URL: `/static/`
   - Directory: `/home/seuusuario/personal/staticfiles`
4. Adicione:
   - URL: `/media/`
   - Directory: `/home/seuusuario/personal/media`

**Troque** `seuusuario` pelo seu username!

---

## 🔄 Passo 8: Recarregar Aplicação

1. Vá em **"Web"** > sua aplicação
2. Clique no botão verde **"Reload seuusuario.pythonanywhere.com"**
3. Aguarde alguns segundos

---

## ✅ Passo 9: Testar

1. Acesse: `https://seuusuario.pythonanywhere.com`
2. Teste o login
3. Teste adicionar produto ao carrinho
4. Teste checkout com Mercado Pago (use cartões de teste)
5. Verifique webhooks e logs

---

## 🔍 Verificar Logs de Erro

Se algo der errado:

1. Vá em **"Web"** > sua aplicação
2. Role até **"Log files"**
3. Veja:
   - **Error log**: erros do servidor
   - **Server log**: logs gerais
   - **Access log**: acessos

Ou no **Bash Console**:

```bash
tail -f ~/personal/logs/mercadopago.log
tail -f ~/personal/logs/security.log
```

---

## 🔄 Atualizar Código (Depois)

Para atualizar o código no futuro:

```bash
# No Bash Console
cd ~/personal
git pull origin main

source ~/personal-venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Recarregar: Web > Reload
```

---

## 🧪 Testar Mercado Pago em Produção

### Cartões de teste:
- **Aprovado**: 5031 4332 1540 6351 (CVV: 123, qualquer data futura)
- **Recusado**: 5031 7557 3453 0604

### Dados do comprador de teste:
- CPF: 123.456.789-00
- Email: test_user_123@testuser.com

Mais cartões: https://www.mercadopago.com.br/developers/pt/docs/testing

---

## 🔐 Segurança

### ✅ Checklist de Segurança:

- [ ] `DJANGO_ENV=production` no arquivo `.env`
- [ ] `SECRET_KEY` única e segura (gere em https://djecrety.ir/)
- [ ] Credenciais de **PRODUÇÃO** do Mercado Pago
- [ ] Arquivo `.env` **NÃO commitado** no Git
- [ ] HTTPS ativo (PythonAnywhere já fornece)

---

## 📞 Suporte

### Mercado Pago:
- https://www.mercadopago.com.br/developers/pt/support

### PythonAnywhere:
- https://help.pythonanywhere.com/
- Forum: https://www.pythonanywhere.com/forums/

---

## 🎯 Resumo Rápido

```bash
# 1. No PythonAnywhere Bash Console
git clone seu-repo personal
cd personal
python3.10 -m venv ../personal-venv
source ../personal-venv/bin/activate
pip install -r requirements.txt

# 2. Criar .env com DJANGO_ENV=production

# 3. Migrar banco
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput

# 4. Configurar WSGI (Web > WSGI file)

# 5. Configurar Static Files (Web > Static files)

# 6. Reload (Web > Reload)

# 7. Testar! 🎉
```

---

## 🎉 Pronto!

Seu sistema está no ar! Agora você pode:

- ✅ Receber pedidos reais
- ✅ Processar pagamentos com Mercado Pago
- ✅ Liberar acesso automático aos produtos
- ✅ Gerenciar tudo pelo admin do Django

**Boas vendas! 💰**
