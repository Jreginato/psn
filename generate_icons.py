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
    """Redimensiona a imagem base 7.png para o tamanho desejado"""
    base_path = os.path.join(OUTPUT_DIR, '7.png')
    if not os.path.exists(base_path):
        raise FileNotFoundError(f"Imagem base '7.png' não encontrada em {OUTPUT_DIR}")
    img = Image.open(base_path).convert('RGBA')
    img = img.resize((size, size), Image.LANCZOS)
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
