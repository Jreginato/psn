// PWA - Service Worker Registration and Install Prompt
let deferredPrompt;
let installButton;

// Registrar Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/service-worker.js')
      .then(registration => {
        console.log('✅ Service Worker registrado com sucesso:', registration.scope);
        
        // Verificar atualizações
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // Nova versão disponível
              showUpdateNotification();
            }
          });
        });
      })
      .catch(error => {
        console.error('❌ Erro ao registrar Service Worker:', error);
      });
  });
}

// Capturar evento de instalação do PWA
window.addEventListener('beforeinstallprompt', (e) => {
  // Prevenir o prompt automático
  e.preventDefault();
  // Guardar o evento para usar depois
  deferredPrompt = e;
  // Mostrar botão de instalação
  showInstallPromotion();
});

// Mostrar promoção de instalação
function showInstallPromotion() {
  // Criar botão de instalação se não existir
  if (!document.getElementById('pwa-install-banner')) {
    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.style.cssText = `
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: linear-gradient(135deg, #10b981 0%, #059669 100%);
      color: white;
      padding: 16px 24px;
      border-radius: 12px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
      z-index: 10000;
      display: flex;
      align-items: center;
      gap: 16px;
      max-width: 90%;
      animation: slideUp 0.3s ease-out;
    `;

    banner.innerHTML = `
      <div style="flex: 1;">
        <strong style="display: block; margin-bottom: 4px;">📱 Instale nosso App!</strong>
        <span style="font-size: 14px; opacity: 0.95;">Acesse mais rápido e receba notificações</span>
      </div>
      <button id="pwa-install-button" style="
        background: white;
        color: #10b981;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        font-size: 14px;
        white-space: nowrap;
      ">Instalar</button>
      <button id="pwa-dismiss-button" style="
        background: transparent;
        color: white;
        border: none;
        padding: 10px;
        cursor: pointer;
        font-size: 20px;
        opacity: 0.8;
      ">×</button>
    `;

    // Adicionar animação
    const style = document.createElement('style');
    style.textContent = `
      @keyframes slideUp {
        from {
          transform: translateX(-50%) translateY(150%);
          opacity: 0;
        }
        to {
          transform: translateX(-50%) translateY(0);
          opacity: 1;
        }
      }
    `;
    document.head.appendChild(style);

    document.body.appendChild(banner);

    // Botão de instalar
    installButton = document.getElementById('pwa-install-button');
    installButton.addEventListener('click', installPWA);

    // Botão de dispensar
    document.getElementById('pwa-dismiss-button').addEventListener('click', () => {
      banner.style.animation = 'slideUp 0.3s ease-out reverse';
      setTimeout(() => banner.remove(), 300);
      // Guardar que o usuário dispensou (não mostrar por 7 dias)
      localStorage.setItem('pwa-dismissed', Date.now());
    });

    // Verificar se foi dispensado recentemente
    const dismissed = localStorage.getItem('pwa-dismissed');
    if (dismissed && Date.now() - parseInt(dismissed) < 7 * 24 * 60 * 60 * 1000) {
      banner.remove();
    }
  }
}

// Instalar PWA
async function installPWA() {
  if (!deferredPrompt) {
    return;
  }

  // Mostrar prompt de instalação
  deferredPrompt.prompt();

  // Aguardar resposta do usuário
  const { outcome } = await deferredPrompt.userChoice;
  console.log(`Resultado da instalação: ${outcome}`);

  if (outcome === 'accepted') {
    console.log('✅ PWA instalado com sucesso!');
  } else {
    console.log('❌ Instalação cancelada pelo usuário');
  }

  // Limpar o prompt
  deferredPrompt = null;

  // Remover banner
  const banner = document.getElementById('pwa-install-banner');
  if (banner) {
    banner.remove();
  }
}

// Detectar quando o app foi instalado
window.addEventListener('appinstalled', (evt) => {
  console.log('✅ App instalado com sucesso!');
  // Remover banner se ainda estiver visível
  const banner = document.getElementById('pwa-install-banner');
  if (banner) {
    banner.remove();
  }
  // Mostrar mensagem de sucesso
  showSuccessMessage();
});

// Mensagem de sucesso
function showSuccessMessage() {
  const message = document.createElement('div');
  message.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #10b981;
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    z-index: 10001;
    animation: slideDown 0.3s ease-out;
  `;
  message.textContent = '✅ App instalado! Agora você pode acessá-lo pela tela inicial.';
  
  document.body.appendChild(message);
  
  setTimeout(() => {
    message.style.animation = 'slideDown 0.3s ease-out reverse';
    setTimeout(() => message.remove(), 300);
  }, 3000);
}

// Notificação de atualização disponível
function showUpdateNotification() {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #3b82f6;
    color: white;
    padding: 16px 24px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    z-index: 10001;
    display: flex;
    align-items: center;
    gap: 16px;
  `;
  
  notification.innerHTML = `
    <span>🔄 Nova versão disponível!</span>
    <button id="update-button" style="
      background: white;
      color: #3b82f6;
      border: none;
      padding: 8px 16px;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
    ">Atualizar</button>
  `;
  
  document.body.appendChild(notification);
  
  document.getElementById('update-button').addEventListener('click', () => {
    window.location.reload();
  });
}

// Detectar se está rodando como PWA
function isPWA() {
  return window.matchMedia('(display-mode: standalone)').matches || 
         window.navigator.standalone || 
         document.referrer.includes('android-app://');
}

// Adicionar classe ao body se for PWA
if (isPWA()) {
  document.documentElement.classList.add('pwa-mode');
  console.log('🚀 Rodando como PWA instalado!');
}

// Status de conexão
window.addEventListener('online', () => {
  console.log('✅ Conexão restaurada');
  showConnectionStatus('online');
});

window.addEventListener('offline', () => {
  console.log('⚠️ Sem conexão - modo offline');
  showConnectionStatus('offline');
});

function showConnectionStatus(status) {
  const existing = document.getElementById('connection-status');
  if (existing) existing.remove();

  const message = document.createElement('div');
  message.id = 'connection-status';
  message.style.cssText = `
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: ${status === 'online' ? '#10b981' : '#ef4444'};
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    z-index: 10001;
    font-size: 14px;
    animation: slideDown 0.3s ease-out;
  `;
  message.textContent = status === 'online' ? '✅ Online' : '⚠️ Modo Offline';
  
  document.body.appendChild(message);
  
  setTimeout(() => {
    message.style.animation = 'slideDown 0.3s ease-out reverse';
    setTimeout(() => message.remove(), 300);
  }, 2000);
}
