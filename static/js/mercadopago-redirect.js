/**
 * Script de fallback para redirecionar depois do Mercado Pago
 * Se o auto_return não funcionar, este script vai redirecionar manualmente
 */

(function() {
    // Verifica se estamos em uma página de sucesso/aprovação do Mercado Pago
    const url = window.location.href;
    const isSuccessPage = url.includes('congrats') && url.includes('approved');
    
    if (!isSuccessPage) {
        return; // Não está na página de sucesso do MP
    }

    // Tira o preference_id da URL
    const urlParams = new URLSearchParams(window.location.search);
    const preferenceId = urlParams.get('preference_id');
    
    if (!preferenceId) {
        console.warn('Não foi possível extrair preference_id da URL');
        return;
    }

    console.log('Detectado sucesso no Mercado Pago. Preference ID:', preferenceId);
    
    // Faz uma requisição para obter o pedido_id baseado no preference_id
    // (assumindo que você tem um endpoint que faz isso)
    fetch('/checkout/redirect-fallback/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({
            preference_id: preferenceId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect_url) {
            console.log('Redirecionando para:', data.redirect_url);
            window.location.href = data.redirect_url;
        } else if (data.message) {
            console.error('Erro:', data.message);
        }
    })
    .catch(error => {
        console.error('Erro ao solicitar redirecionamento:', error);
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
})();
