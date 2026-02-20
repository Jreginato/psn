# 🔧 Configuração de Ambiente (DEV vs PROD)

## 📌 Visão Geral

O sistema agora possui **configuração automática** que muda entre **desenvolvimento** e **produção** baseado em uma única variável de ambiente: `DJANGO_ENV`.

---

## 🎯 Como Funciona

### Variável de Controle: `DJANGO_ENV`

```bash
# Desenvolvimento (padrão)
DJANGO_ENV=development

# Produção
DJANGO_ENV=production
```

---

## 🔄 O que Muda Automaticamente

### 💻 **Modo DESENVOLVIMENTO** (`DJANGO_ENV=development`)

✅ **Debug Mode**: `DEBUG = True`  
✅ **Hosts**: Aceita qualquer host (`ALLOWED_HOSTS = ['*']`)  
✅ **Banco de Dados**: SQLite local (`db.sqlite3`)  
✅ **Secret Key**: Pode usar padrão (nunca use em produção!)  
✅ **Segurança HTTPS**: Desativada (para testar localmente)  
✅ **Static Root**: Não necessário  

**🔐 Mercado Pago - TESTE:**
- ✅ Credenciais de **TESTE** (`TEST-...`)
- ✅ Modo: `test` / `sandbox`
- ✅ Login **obrigatório** (não aceita convidados)
- ✅ Checkout Point: `sandbox_init_point`
- ✅ Pagamentos: **NÃO são cobrados** (simulação)

---

### 🚀 **Modo PRODUÇÃO** (`DJANGO_ENV=production`)

✅ **Debug Mode**: `DEBUG = False`  
✅ **Hosts**: Apenas domínios específicos (PythonAnywhere, etc)  
✅ **Banco de Dados**: SQLite (`db.sqlite3`)  
✅ **Secret Key**: Lida de variável de ambiente (segura)  
✅ **Segurança HTTPS**: Ativada automaticamente  
✅ **Static Root**: `staticfiles/` (para `collectstatic`)  

**💳 Mercado Pago - PRODUÇÃO:**
- ✅ Credenciais de **PRODUÇÃO** (`APP-USR-...`)
- ✅ Modo: `prod` / `production`
- ✅ **Modo convidado** ativo (compra sem cadastro)
- ✅ Checkout Point: `init_point`
- ✅ Pagamentos: **COBRADOS DE VERDADE** 💰

---

## 🛠️ Configuração Local (Desenvolvimento)

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

**Opção 1 - Arquivo .env (mais prático):**
```bash
# Copiar exemplo
cp .env.development .env
# Editar com suas credenciais
```

**Opção 2 - Variáveis do sistema:**
```bash
# Windows (CMD)
set DJANGO_ENV=development
set MP_ACCESS_TOKEN_TEST=TEST-seu-token

# Linux/Mac
export DJANGO_ENV=development
export MP_ACCESS_TOKEN_TEST=TEST-seu-token
```

### 3. Editar configurações

```bash
# ===== DESENVOLVIMENTO =====
DJANGO_ENV=development

# Django
SECRET_KEY=dev-secret-key-qualquer-coisa

# Mercado Pago - TESTE
MP_ACCESS_TOKEN_TEST=TEST-seu-token-de-teste
MP_PUBLIC_KEY_TEST=TEST-sua-key-de-teste
```

### 4. Obter credenciais de TESTE do Mercado Pago

1. Acesse: https://www.mercadopago.com.br/developers/panel
2. Vá em: **"Suas integrações"** > **"Credenciais"**
3. Escolha: **"Credenciais de teste"**
4. Copie:
   - **Access Token** (começa com `TEST-`)
   - **Public Key** (começa com `TEST-`)
5. Cole no `.env`

### 5. Rodar localmente

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

✅ Agora você está em **modo DESENVOLVIMENTO**!

---

## ☁️ Configuração no PythonAnywhere (Produção)

### 1. Criar arquivo `.env` no servidor

No **Bash Console** do PythonAnywhere:

```bash
cd ~/personal
nano .env
```

### 2. Configurar para **PRODUÇÃO**

```bash
# ===== PRODUÇÃO =====
DJANGO_ENV=production

# Django
SECRET_KEY=SUA-SECRET-KEY-UNICA-E-SEGURA-GERADA
ALLOWED_HOST=seusite.pythonanywhere.com

# Mercado Pago - PRODUÇÃO
MP_ACCESS_TOKEN_PROD=APP-USR-seu-token-real-de-producao
MP_PUBLIC_KEY_PROD=APP-USR-sua-public-key-de-producao
```

**Nota:** O sistema usa SQLite (db.sqlite3) em todos os ambientes.

### 3. Obter credenciais de PRODUÇÃO do Mercado Pago

1. Acesse: https://www.mercadopago.com.br/developers/panel
2. Vá em: **"Suas integrações"** > **"Credenciais"**
3. Escolha: **"Credenciais de produção"** (não de teste!)
4. Copie:
   - **Access Token** (começa com `APP-USR-`)
   - **Public Key** (começa com `APP-USR-`)
5. Cole no `.env` do servidor

### 4. Configurar WSGI

Edite o arquivo WSGI do PythonAnywhere com:

```python
import os
import sys

# Path do projeto
path = '/home/seuusuario/personal'  # MUDE 'seuusuario'
sys.path.insert(0, path)

# Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'personal.settings'

# Definir variáveis de ambiente diretamente (substitua pelos valores reais)
os.environ['DJANGO_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'sua-secret-key-segura'
os.environ['ALLOWED_HOST'] = 'seuusuario.pythonanywhere.com'
os.environ['MP_ACCESS_TOKEN_PROD'] = 'APP-USR-seu-token-real'
os.environ['MP_PUBLIC_KEY_PROD'] = 'APP-USR-sua-key-real'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Ou carregue de um arquivo .env:**
```python
# ... código acima ...

# Carregar .env manualmente
with open('/home/seuusuario/personal/.env') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ.setdefault(key, value)

# ... resto do código ...
```

### 5. Migrar e coletar estáticos

```bash
source ~/personal-venv/bin/activate
cd ~/personal
python manage.py migrate
python manage.py collectstatic --noinput
```

### 6. Reload

No dashboard Web do PythonAnywhere, clique em **"Reload"**.

✅ Agora você está em **modo PRODUÇÃO**!

---

## 🧪 Testar Configuração

### Ver ambiente atual:

```bash
python manage.py shell
```

```python
from django.conf import settings

print(f"Ambiente: {settings.ENVIRONMENT}")
print(f"É Produção? {settings.IS_PRODUCTION}")
print(f"Debug? {settings.DEBUG}")
print(f"Mercado Pago Mode: {settings.MERCADOPAGO_MODE}")
print(f"Test Only? {settings.MERCADOPAGO_TEST_ONLY}")
```

---

## 📋 Checklist de Segurança

### ✅ **Desenvolvimento**:
- [ ] `DJANGO_ENV=development`
- [ ] Credenciais de **TESTE** do Mercado Pago (`TEST-...`)
- [ ] `.env` local (nunca commite!)

### ✅ **Produção**:
- [ ] `DJANGO_ENV=production`
- [ ] `SECRET_KEY` única e forte (https://djecrety.ir/)
- [ ] Credenciais de **PRODUÇÃO** do Mercado Pago (`APP-USR-...`)
- [ ] `ALLOWED_HOST` configurado corretamente
- [ ] HTTPS ativo (PythonAnywhere já fornece)
- [ ] `.env` no servidor (nunca commite!)

---

## 🔄 Alternar Entre Ambientes

### Mudar para Produção:

```bash
# No .env
DJANGO_ENV=production
```

### Voltar para Desenvolvimento:

```bash
# No .env
DJANGO_ENV=development
```

Sempre reinicie o servidor após mudar!

---

## 📁 Arquivos de Referência

- `.env.example` - Template completo com todas as variáveis
- `.env.development` - Template para desenvolvimento
- `.env.production` - Template para produção
- `DEPLOY_PYTHONANYWHERE.md` - Guia completo de deploy

---

## ❓ Perguntas Frequentes

### **Como sei se estou em produção ou desenvolvimento?**

Verifique no shell do Django:

```python
from django.conf import settings
print(settings.IS_PRODUCTION)  # True = produção, False = desenvolvimento
```

### **As credenciais do Mercado Pago mudam sozinhas?**

Sim! O sistema automaticamente usa:
- `MP_ACCESS_TOKEN_TEST` e `MP_PUBLIC_KEY_TEST` em desenvolvimento
- `MP_ACCESS_TOKEN_PROD` e `MP_PUBLIC_KEY_PROD` em produção

### **Posso testar pagamentos em desenvolvimento?**

Sim! Use as credenciais de TESTE e os cartões de teste do Mercado Pago:
- **Aprovado**: 5031 4332 1540 6351
- Mais: https://www.mercadopago.com.br/developers/pt/docs/testing

### **E se eu esquecer de mudar para produção?**

Se você não definir `DJANGO_ENV=production`, o sistema **permanece em desenvolvimento** (comportamento seguro). Sempre verifique no PythonAnywhere se a variável está correta!

---

## 🎉 Pronto!

Agora você tem:
- ✅ Configuração automática por ambiente
- ✅ Mercado Pago em teste/produção automático
- ✅ Segurança ativada em produção
- ✅ Desenvolvimento simplificado

**Desenvolva tranquilo e publique com confiança!** 🚀
