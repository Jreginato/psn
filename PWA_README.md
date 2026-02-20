# 📱 PWA - Progressive Web App

## ✅ Configuração Concluída

Seu projeto Django agora está configurado como PWA! Os usuários poderão instalar o app como aplicativo nativo.

## 🎯 O que foi implementado

### 1. Manifest.json
- ✅ Arquivo de manifesto em `static/manifest.json`
- ✅ Configurações de nome, ícones, cores e atalhos
- ✅ Display mode standalone (app fullscreen)

### 2. Service Worker
- ✅ Cache inteligente de assets estáticos
- ✅ Funcionamento offline
- ✅ Estratégia "Network First" para HTML
- ✅ Estratégia "Cache First" para assets (CSS, JS, imagens)
- ✅ Background sync preparado
- ✅ Push notifications preparado (para futuro)

### 3. Meta Tags PWA
- ✅ Adicionadas em todos os templates principais:
  - `sales.html` (landing page)
  - `base_dashboard.html` (área do cliente)
  - `catalogo.html` (loja)
  - `detalhes.html` (carrinho)

### 4. Script de Instalação
- ✅ Prompt automático de instalação
- ✅ Banner customizado com opção de dispensar
- ✅ Indicador de status online/offline
- ✅ Notificações de atualização

## 📋 Próximos Passos

### 1. Gerar Ícones do PWA

Os ícones são essenciais para o PWA funcionar. Você tem duas opções:

#### Opção A: Script Automático (Recomendado para teste)

```bash
# Instalar Pillow (se ainda não tiver)
pip install Pillow

# Executar o gerador de ícones
python generate_icons.py
```

Isso vai criar ícones placeholder com as iniciais "PT".

#### Opção B: Ícones Profissionais (Recomendado para produção)

1. Crie uma imagem quadrada da sua logo (mínimo 512x512px)
2. Use uma ferramenta online:
   - https://realfavicongenerator.net/
   - https://www.pwabuilder.com/imageGenerator
3. Baixe os ícones nos tamanhos: 72, 96, 128, 144, 152, 192, 384, 512
4. Coloque em `static/icons/` com os nomes:
   - `icon-72x72.png`
   - `icon-96x96.png`
   - `icon-128x128.png`
   - `icon-144x144.png`
   - `icon-152x152.png`
   - `icon-192x192.png`
   - `icon-384x384.png`
   - `icon-512x512.png`

### 2. Testar o PWA

#### Desktop (Chrome/Edge)
1. Execute o servidor: `python manage.py runserver`
2. Abra no navegador: http://localhost:8000
3. Clique no ícone de instalação (➕) na barra de endereços
4. Ou espere o banner automático aparecer

#### Mobile
1. Acesse o site pelo navegador mobile
2. Chrome Android: Menu > "Adicionar à tela inicial"
3. Safari iOS: Compartilhar > "Adicionar à Tela Inicial"

### 3. Verificar Funcionamento

Após instalar:
- ✅ App deve abrir sem barras do navegador
- ✅ Deve funcionar offline (páginas visitadas)
- ✅ Ícone deve aparecer na tela inicial
- ✅ Banner de instalação não deve mais aparecer

### 4. Deployment (Produção)

#### Requisitos para PWA em produção:
1. **HTTPS obrigatório** - PWA só funciona em HTTPS
2. **Service Worker registrado** - Já está configurado
3. **Manifest válido** - Já está configurado
4. **Ícones corretos** - Substitua os placeholders

#### Configurações do Django para produção:

```python
# settings.py

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# CORS (se necessário)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://seudominio.com",
]
```

### 5. Personalização

#### Cores do tema
Edite `static/manifest.json`:
```json
{
  "theme_color": "#10b981",  // Cor da barra superior
  "background_color": "#ffffff"  // Cor de fundo na inicialização
}
```

#### Nome do app
Edite `static/manifest.json`:
```json
{
  "name": "Seu Nome Completo",
  "short_name": "Nome Curto"
}
```

#### Cache do Service Worker
Edite `static/service-worker.js`:
```javascript
const CACHE_NAME = 'personal-trainer-v2';  // Incremente para forçar atualização
```

## 🧪 Testes e Validação

### Chrome DevTools
1. Abra DevTools (F12)
2. Aba "Application"
3. Verifique:
   - ✅ Service Workers → Status "activated"
   - ✅ Manifest → Sem erros
   - ✅ Storage → Cache Storage com arquivos

### Lighthouse
1. DevTools > Lighthouse
2. Selecione "Progressive Web App"
3. Clique "Generate report"
4. Meta: Score > 90

### PWA Builder
- https://www.pwabuilder.com/
- Digite sua URL
- Analise o relatório

## 📱 Funcionalidades Futuras

Já preparadas no código, mas precisam de implementação:

### Push Notifications
```javascript
// Já tem listener no service worker
// Implementar backend para enviar notificações
```

### Background Sync
```javascript
// Já tem listener no service worker
// Útil para sincronizar dados offline
```

### Install Prompts Customizados
```javascript
// Já implementado em pwa.js
// Banner customizado com branding
```

## 🐛 Troubleshooting

### Service Worker não registra
- Verifique console do navegador
- Limpe cache: DevTools > Application > Clear storage
- Service Worker só funciona em HTTPS ou localhost

### Ícones não aparecem
- Verifique se os arquivos existem em `static/icons/`
- Execute `python manage.py collectstatic` em produção
- Limpe cache e recarregue

### PWA não oferece instalação
- Verifique se está em HTTPS (ou localhost)
- Confirme que manifest.json está acessível
- Verificar se service worker está ativo
- Lighthouse pode identificar o problema

### Cache não atualiza
- Incremente `CACHE_NAME` no service-worker.js
- Force refresh: Ctrl+Shift+R
- DevTools > Application > Clear storage

## 📚 Recursos

- [PWA Checklist](https://web.dev/pwa-checklist/)
- [Service Worker API](https://developer.mozilla.org/pt-BR/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://web.dev/add-manifest/)
- [Workbox (Framework PWA)](https://developers.google.com/web/tools/workbox)

## 🎉 Pronto!

Seu app agora é um PWA completo e pode ser instalado como aplicativo nativo em qualquer dispositivo!

Para qualquer dúvida, consulte a documentação ou abra uma issue.
