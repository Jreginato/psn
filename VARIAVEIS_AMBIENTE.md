# 🔧 Como Definir Variáveis de Ambiente

O sistema usa variáveis de ambiente para configuração. Você pode defini-las de várias formas:

---

## 💻 **Desenvolvimento Local**

### Opção 1: Arquivo .env (recomendado)

Crie um arquivo `.env` na raiz do projeto:

```bash
DJANGO_ENV=development
SECRET_KEY=dev-key-qualquer
MP_ACCESS_TOKEN_TEST=TEST-seu-token
MP_PUBLIC_KEY_TEST=TEST-sua-key
```

O Django lê automaticamente com `os.environ.get()`.

### Opção 2: Variáveis do Sistema

**Windows (CMD):**
```cmd
set DJANGO_ENV=development
set MP_ACCESS_TOKEN_TEST=TEST-seu-token
python manage.py runserver
```

**Windows (PowerShell):**
```powershell
$env:DJANGO_ENV="development"
$env:MP_ACCESS_TOKEN_TEST="TEST-seu-token"
python manage.py runserver
```

**Linux/Mac:**
```bash
export DJANGO_ENV=development
export MP_ACCESS_TOKEN_TEST=TEST-seu-token
python manage.py runserver
```

### Opção 3: Definir no comando

**Windows:**
```cmd
set DJANGO_ENV=development && python manage.py runserver
```

**Linux/Mac:**
```bash
DJANGO_ENV=development python manage.py runserver
```

---

## ☁️ **Produção (PythonAnywhere)**

### Opção 1: Arquivo .env

Crie `/home/seuusuario/personal/.env`:

```bash
DJANGO_ENV=production
SECRET_KEY=sua-secret-key-segura
ALLOWED_HOST=seuusuario.pythonanywhere.com
MP_ACCESS_TOKEN_PROD=APP-USR-seu-token
MP_PUBLIC_KEY_PROD=APP-USR-sua-key
```

No arquivo WSGI, carregue manualmente:

```python
# Carregar .env
with open('/home/seuusuario/personal/.env') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ.setdefault(key, value)
```

### Opção 2: Direto no WSGI (mais simples)

No arquivo WSGI do PythonAnywhere:

```python
import os

# Definir variáveis diretamente
os.environ['DJANGO_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'sua-secret-key-segura'
os.environ['ALLOWED_HOST'] = 'seuusuario.pythonanywhere.com'
os.environ['MP_ACCESS_TOKEN_PROD'] = 'APP-USR-seu-token'
os.environ['MP_PUBLIC_KEY_PROD'] = 'APP-USR-sua-key'
```

---

## 📋 Variáveis Disponíveis

### Obrigatórias:

| Variável | Desenvolvimento | Produção |
|----------|----------------|----------|
| `DJANGO_ENV` | `development` | `production` |
| `MP_ACCESS_TOKEN_TEST` | Seu token teste | - |
| `MP_PUBLIC_KEY_TEST` | Sua key teste | - |
| `MP_ACCESS_TOKEN_PROD` | - | Seu token prod |
| `MP_PUBLIC_KEY_PROD` | - | Sua key prod |

### Opcionais:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `SECRET_KEY` | Padrão do código | Secret key do Django |
| `ALLOWED_HOST` | `*` (dev) / erro (prod) | Domínio permitido |

---

## 🧪 Testar Configuração

```python
python manage.py shell
```

```python
import os
from django.conf import settings

print(f"DJANGO_ENV: {os.environ.get('DJANGO_ENV')}")
print(f"IS_PRODUCTION: {settings.IS_PRODUCTION}")
print(f"MP Token: {settings.MERCADOPAGO_ACCESS_TOKEN[:20]}...")
```

---

## ⚠️ Segurança

✅ **Desenvolvimento:** Pode usar valores fixos ou arquivo .env  
✅ **Produção:** Sempre use variáveis de ambiente (nunca hardcode)  
❌ **NUNCA** commite arquivos .env no Git (já está no .gitignore)  

---

## 💡 Dica

Use o arquivo `.env.development` ou `.env.production` como template:

```bash
# Copiar template
cp .env.development .env

# Editar suas credenciais
nano .env
```
