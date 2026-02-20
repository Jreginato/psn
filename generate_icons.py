"""
Script para gerar ícones PWA placeholder
Execute: python generate_icons.py

Este script cria ícones em diferentes tamanhos para o PWA.
Você pode substituir estes ícones por sua logo real depois.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Tamanhos de ícones necessários para PWA
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Diretório de saída
OUTPUT_DIR = 'static/icons'

# Cores do tema (verde do Personal Trainer)
BG_COLOR = '#10b981'  # Verde primário
TEXT_COLOR = '#ffffff'  # Branco

def create_icon(size):
    """Cria um ícone quadrado com o logo/iniciais"""
    # Criar imagem
    img = Image.new('RGB', (size, size), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Texto a ser desenhado (iniciais)
    text = "PT"
    
    # Tentar usar fonte do sistema, se não houver, usar fonte padrão
    try:
        # Tamanho da fonte proporcional ao ícone
        font_size = int(size * 0.4)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fonte padrão se não encontrar Arial
        font = ImageFont.load_default()
    
    # Obter tamanho do texto
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Centralizar texto
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]
    
    # Desenhar círculo de fundo (opcional)
    margin = size // 10
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill='#059669',  # Verde mais escuro
        outline=TEXT_COLOR,
        width=max(2, size // 100)
    )
    
    # Desenhar texto
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)
    
    return img

def main():
    """Gera todos os ícones necessários"""
    # Criar diretório se não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("🎨 Gerando ícones PWA...")
    
    for size in ICON_SIZES:
        icon = create_icon(size)
        filename = f'icon-{size}x{size}.png'
        filepath = os.path.join(OUTPUT_DIR, filename)
        icon.save(filepath, 'PNG')
        print(f'✅ Criado: {filename}')
    
    print(f"\n✨ Todos os ícones foram criados em '{OUTPUT_DIR}'")
    print("\n💡 Dica: Substitua estes ícones pela sua logo real para personalizar o PWA")
    print("   Use uma ferramenta como https://realfavicongenerator.net/ para criar ícones profissionais")

if __name__ == '__main__':
    main()
