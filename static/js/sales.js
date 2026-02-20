const topbar = document.getElementById('topbar');
const faqItems = document.querySelectorAll('.faq-item');
const ctaButtons = document.querySelectorAll('[data-cta]');

const whatsappNumber = '5511999999999';
const checkoutLinks = {
    treino_objetivo: 'https://pay.kiwify.com.br/SEU-LINK-TREINO-OBJETIVO',
    ebooks: 'https://pay.kiwify.com.br/SEU-LINK-EBOOKS',
    cursos: 'https://pay.kiwify.com.br/SEU-LINK-CURSOS',
};

window.addEventListener('scroll', () => {
    if (window.scrollY > 8) {
        topbar.classList.add('scrolled');
    } else {
        topbar.classList.remove('scrolled');
    }
});

faqItems.forEach((item) => {
    const button = item.querySelector('.faq-question');

    button.addEventListener('click', () => {
        const isOpen = item.classList.contains('open');

        faqItems.forEach((currentItem) => currentItem.classList.remove('open'));

        if (!isOpen) {
            item.classList.add('open');
        }
    });
});

ctaButtons.forEach((button) => {
    button.addEventListener('click', (event) => {
        event.preventDefault();

        const ctaType = button.dataset.cta;

        if (ctaType === 'whatsapp') {
            const service = button.dataset.service || 'atendimento';
            const message = encodeURIComponent(`Olá! Tenho interesse em ${service}. Pode me passar mais detalhes?`);
            const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${message}`;

            window.open(whatsappUrl, '_blank', 'noopener,noreferrer');
            return;
        }

        if (ctaType === 'checkout') {
            const product = button.dataset.product || '';
            const checkoutUrl = checkoutLinks[product];

            if (checkoutUrl) {
                window.open(checkoutUrl, '_blank', 'noopener,noreferrer');
            }
        }
    });
});
