# ⚙️ REFERÊNCIA RÁPIDA - VARIÁVEIS DE AMBIENTE

## 🎯 Variável Principal

```bash
DJANGO_ENV=development  # ou 'production'
```

---

## 📋 Resumo das Diferenças

| Configuração | Desenvolvimento | Produção |
|-------------|-----------------|----------|
| **DEBUG** | `True` | `False` |
| **ALLOWED_HOSTS** | `['*']` | Domínios específicos |
| **Banco de Dados** | SQLite | SQLite |
| **SECRET_KEY** | Pode ser fixa | De variável de ambiente |
| **HTTPS** | Desativado | Ativado |
| **Mercado Pago Tokens** | `TEST-...` | `APP-USR-...` |
| **Mercado Pago Mode** | `test` / `sandbox` | `prod` / `production` |
| **Mercado Pago Test Only** | `True` (login obrig.) | `False` (modo convidado) |
| **Checkout Point** | `sandbox_init_point` | `init_point` |
| **Pagamentos** | Simulados (grátis) | Reais (cobrados) |

---

## 🔐 Variáveis de Ambiente Necessárias

### **DESENVOLVIMENTO** (.env local)

```bash
DJANGO_ENV=development
SECRET_KEY=dev-key-qualquer
MP_ACCESS_TOKEN_TEST=TEST-1234...
MP_PUBLIC_KEY_TEST=TEST-abc...
```

### **PRODUÇÃO** (.env no servidor)

```bash
DJANGO_ENV=production
SECRET_KEY=chave-unica-super-segura
ALLOWED_HOST=seusite.pythonanywhere.com
MP_ACCESS_TOKEN_PROD=APP-USR-1234...
MP_PUBLIC_KEY_PROD=APP-USR-abc...
```

**Nota:** O sistema usa SQLite (db.sqlite3) em todos os ambientes.

---

## 🧪 Testar Configuração Atual

```python
# No shell do Django
python manage.py shell

from django.conf import settings
print(f"Ambiente: {settings.ENVIRONMENT}")
print(f"Produção? {settings.IS_PRODUCTION}")
print(f"MP Mode: {settings.MERCADOPAGO_MODE}")
```

---

## 📁 Arquivos de Ajuda

- `CONFIGURACAO_AMBIENTE.md` - Guia completo de configuração
- `DEPLOY_PYTHONANYWHERE.md` - Passo a passo de deploy
- `.env.example` - Template de variáveis
- `.env.development` - Template para dev
- `.env.production` - Template para prod

---

## ⚠️ IMPORTANTE

1. **NUNCA** commite o arquivo `.env` no Git
2. Use credenciais de **TESTE** em desenvolvimento
3. Use credenciais de **PRODUÇÃO** apenas no servidor
4. Gere uma `SECRET_KEY` única para produção: https://djecrety.ir/
