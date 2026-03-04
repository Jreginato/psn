"""
Script de seed: Curso Emagrecimento - R$ 19,90
Cria o produto + 45 aulas organizadas em 5 módulos.

Uso:
    python seed_curso_emagrecimento.py
"""

import os
import sys
import django

# ── Configuração do Django ─────────────────────────────────────────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "personal.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# ── Imports dos modelos ────────────────────────────────────────────────────────
from decimal import Decimal
from produtos.models import Categoria, Produto, ConteudoDigital

# ── 1. Categoria ───────────────────────────────────────────────────────────────
categoria, _ = Categoria.objects.get_or_create(
    slug="cursos",
    defaults={
        "nome": "Cursos",
        "descricao": "Cursos digitais de saúde, fitness e bem-estar",
        "icone": "fa-play-circle",
        "ordem": 1,
        "ativo": True,
    },
)
print(f"[OK] Categoria: {categoria.nome}")

# ── 2. Produto ─────────────────────────────────────────────────────────────────
produto, created = Produto.objects.get_or_create(
    slug="curso-emagrecimento-definitivo",
    defaults={
        "nome": "Emagrecimento Definitivo",
        "categoria": categoria,
        "preco": Decimal("19.90"),
        # Hero
        "titulo_hero": "Emagreça de verdade, de uma vez por todas",
        "subtitulo_hero": (
            "Método prático e direto ao ponto para você perder gordura, "
            "ganhar disposição e transformar seu corpo — sem passar fome "
            "e sem dietas impossíveis."
        ),
        # Introdução
        "texto_introducao": (
            "Se você já tentou de tudo e não conseguiu resultado, o problema "
            "não é você, é o método. Neste curso você vai aprender, de forma "
            "simples e aplicável, como o corpo realmente queima gordura e como "
            "usar isso a seu favor no dia a dia."
        ),
        # Inclusos
        "item_incluso_1": "45 aulas em vídeo organizadas em 5 módulos",
        "item_incluso_2": "Planilha de controle alimentar editável",
        "item_incluso_3": "Plano de treino para iniciantes e intermediários",
        "item_incluso_4": "Guia de compras saudáveis e lista de substituições",
        "item_incluso_5": "Acesso vitalício com atualizações gratuitas",
        # Para quem é
        "para_quem_titulo": "Para quem é este curso?",
        "para_quem_texto": (
            "Para qualquer pessoa que queira perder gordura de forma saudável, "
            "sem modismos ou restrições absurdas. Iniciantes ou quem já tentou "
            "outras abordagens e não obteve resultados duradouros."
        ),
        # Benefícios
        "beneficio_1_titulo": "Queime gordura com ciência",
        "beneficio_1_descricao": (
            "Entenda como o metabolismo funciona e aplique estratégias "
            "baseadas em evidências para acelerar a perda de gordura."
        ),
        "beneficio_2_titulo": "Alimentação sem sofrimento",
        "beneficio_2_descricao": (
            "Aprenda a montar refeições saborosas e completas que cabem "
            "na sua rotina e no seu bolso."
        ),
        "beneficio_3_titulo": "Resultados que duram",
        "beneficio_3_descricao": (
            "Construa hábitos sólidos que vão além da dieta e mantêm o "
            "resultado para sempre."
        ),
        # Garantia e CTA
        "texto_garantia": "7 dias de garantia incondicional. Não gostou, devolvemos 100% do seu dinheiro.",
        "texto_cta": "Quero Emagrecer Agora",
        "status": "publicado",
        "destaque": True,
        "ordem": 1,
    },
)

if not created:
    print(f"[ATENÇÃO] Produto já existe: {produto.nome}. Aulas serão adicionadas se não existirem.")
else:
    print(f"[OK] Produto criado: {produto.nome} — R$ {produto.preco}")

# ── 3. Aulas ───────────────────────────────────────────────────────────────────
# Estrutura: (ordem, titulo, descricao, duracao, tipo)

AULAS = [
    # ── MÓDULO 1: FUNDAMENTOS DO EMAGRECIMENTO (aulas 1-9) ────────────────────
    (1,  "Boas-vindas e como aproveitar o curso ao máximo",
         "Visão geral do método, estrutura das aulas e como extrair o melhor resultado.",
         "8min", "video_url"),

    (2,  "Como o corpo realmente queima gordura",
         "Mecanismos fisiológicos da lipólise explicados de forma simples e aplicável.",
         "14min", "video_url"),

    (3,  "Por que dietas falham — e o que fazer diferente",
         "Os erros mais comuns de quem tenta emagrecer e como evitá-los definitivamente.",
         "12min", "video_url"),

    (4,  "Déficit calórico: o único princípio que você precisa entender",
         "O que é, como calcular e como criar um déficit sustentável sem passar fome.",
         "15min", "video_url"),

    (5,  "Calculando seu gasto energético diário (TDEE)",
         "Passo a passo para descobrir quantas calorias você gasta e quantas deve consumir.",
         "10min", "video_url"),

    (6,  "Metabolismo lento: mito ou realidade?",
         "A verdade sobre adaptação metabólica e como evitar o efeito platô.",
         "11min", "video_url"),

    (7,  "Hormonios e emagrecimento: insulina, cortisol e leptina",
         "Como os principais hormônios influenciam o acúmulo e a queima de gordura.",
         "13min", "video_url"),

    (8,  "A importância do peso vs. composição corporal",
         "Por que a balança mente e como medir o progresso real.",
         "9min", "video_url"),

    (9,  "Definindo sua meta de forma inteligente",
         "Como estabelecer metas realistas, mensuráveis e motivadoras.",
         "8min", "video_url"),

    # ── MÓDULO 2: ALIMENTAÇÃO INTELIGENTE (aulas 10-19) ───────────────────────
    (10, "Os três macronutrientes explicados",
         "Proteínas, carboidratos e gorduras: funções, fontes e quantidades ideais.",
         "16min", "video_url"),

    (11, "Proteínas: a chave para preservar músculo e saciar",
         "Por que proteínas são fundamentais no emagrecimento e como garantir o consumo adequado.",
         "13min", "video_url"),

    (12, "Carboidratos não são vilões — aprenda a usá-los",
         "Como distribuir carboidratos ao longo do dia para ter energia e perder gordura.",
         "12min", "video_url"),

    (13, "Gorduras boas: quais incluir na dieta e por quê",
         "Ômega-3, azeite, abacate e castanhas — aliados da saúde e do emagrecimento.",
         "11min", "video_url"),

    (14, "Montando seu prato de forma prática (método do prato)",
         "Modelo visual e simples para montar refeições equilibradas sem contar calorias.",
         "10min", "video_url"),

    (15, "Lista de alimentos termogênicos naturais",
         "Alimentos que aumentam levemente o gasto calórico e como incluí-los na rotina.",
         "9min", "video_url"),

    (16, "Como ler rótulos e não ser enganado",
         "Entenda as informações nutricionais e identifique produtos ultraprocessados.",
         "12min", "video_url"),

    (17, "Guia prático de substituições inteligentes",
         "Troque alimentos calóricos por opções saborosas e nutritivas sem sofrimento.",
         "10min", "video_url"),

    (18, "Planejamento semanal de refeições (meal prep)",
         "Como organizar suas refeições da semana em poucas horas e manter a dieta no piloto automático.",
         "14min", "video_url"),

    (19, "Alimentação fora de casa: como fazer boas escolhas no restaurante",
         "Estratégias para manter o plano alimentar em eventos sociais, viagens e restaurantes.",
         "11min", "video_url"),

    # ── MÓDULO 3: TREINOS PARA EMAGRECER (aulas 20-29) ────────────────────────
    (20, "Exercício e emagrecimento: o papel real da atividade física",
         "O quanto o treino contribui para o déficit calórico e por que musculação é essencial.",
         "12min", "video_url"),

    (21, "Musculação vs. cardio: o que é melhor para emagrecer?",
         "Comparativo científico e como combinar os dois para resultados máximos.",
         "13min", "video_url"),

    (22, "Treino HIIT: queime gordura em menos tempo",
         "O que é o HIIT, seus benefícios para o metabolismo e como montar um protocolo.",
         "14min", "video_url"),

    (23, "Plano de treino para iniciantes — Semana 1 a 4",
         "Programa completo com exercícios, séries, repetições e tempo de descanso.",
         "16min", "video_url"),

    (24, "Plano de treino intermediário — Semana 5 a 8",
         "Progressão de carga e volume para continuar evoluindo após o nível inicial.",
         "15min", "video_url"),

    (25, "Treinos em casa sem equipamento",
         "Rotina eficiente com peso corporal para quem não tem academia ou equipamentos.",
         "13min", "video_url"),

    (26, "A importância do NEAT (gasto calórico fora do treino)",
         "Como aumentar a queima de calorias ao longo do dia com pequenas mudanças de comportamento.",
         "9min", "video_url"),

    (27, "Alongamento e mobilidade: como evitar lesões e acelerar resultados",
         "Rotina de 10 minutos de mobilidade que todo praticante deve fazer.",
         "10min", "video_url"),

    (28, "Como progredir nos treinos e evitar o platô",
         "Princípios de sobrecarga progressiva aplicados ao emagrecimento.",
         "11min", "video_url"),

    (29, "Recuperação muscular e treino na semana",
         "Quantos dias treinar, como distribuir os grupos musculares e o papel do descanso.",
         "10min", "video_url"),

    # ── MÓDULO 4: HÁBITOS, COMPORTAMENTO E MENTALIDADE (aulas 30-37) ──────────
    (30, "O papel da mente no emagrecimento",
         "Gatilhos emocionais, comer por ansiedade e como desenvolver uma relação saudável com comida.",
         "13min", "video_url"),

    (31, "Sono e emagrecimento: a conexão que ninguém te contou",
         "Como a privação de sono sabota a queima de gordura e aumenta o apetite.",
         "12min", "video_url"),

    (32, "Gerenciamento do estresse para emagrecer",
         "Técnicas simples de controle do cortisol que evitam o acúmulo de gordura abdominal.",
         "11min", "video_url"),

    (33, "Mindful eating: coma com atenção e emagreça naturalmente",
         "Como comer devagar e conscientemente ajuda a reduzir calorias sem esforço.",
         "10min", "video_url"),

    (34, "Como lidar com recaídas sem sabotar tudo",
         "Estratégias psicológicas para voltar ao trilho rapidamente após um deslize.",
         "9min", "video_url"),

    (35, "Hidratação: quanto e como beber água para emagrecer",
         "O papel da água no metabolismo, na saciedade e na performance nos treinos.",
         "8min", "video_url"),

    (36, "Construindo uma rotina sustentável de emagrecimento",
         "Como criar hábitos diários que tornam o emagrecimento automático e duradouro.",
         "12min", "video_url"),

    (37, "Redes sociais, comparações e autoestima durante o processo",
         "Como proteger sua motivação e manter o foco sem se comparar com os outros.",
         "9min", "video_url"),

    # ── MÓDULO 5: SUPLEMENTAÇÃO E ACELERAÇÃO DOS RESULTADOS (aulas 38-43) ─────
    (38, "Suplementação: precisa mesmo? A verdade sem mimimi",
         "Quais suplementos têm evidência científica para emagrecimento e quais são mito.",
         "13min", "video_url"),

    (39, "Whey protein: para quem, quando e como usar",
         "Principais benefícios, tipos e o momento certo de consumo.",
         "11min", "video_url"),

    (40, "Cafeína, creatina e termogênicos: vale a pena?",
         "Análise honesta dos suplementos mais populares do mercado fitness.",
         "12min", "video_url"),

    (41, "Jejum intermitente: funciona para todo mundo?",
         "Prós, contras e como aplicar o jejum de forma inteligente no seu protocolo.",
         "14min", "video_url"),

    (42, "Low carb e keto: quando usar e quando evitar",
         "Entenda as dietas low carb, para quem elas funcionam e os principais equívocos.",
         "13min", "video_url"),

    (43, "Dieta reversa: como sair do déficit sem engordar tudo de volta",
         "O protocolo correto para terminar o cutting e manter o peso conquistado.",
         "11min", "video_url"),

    # ── BÔNUS (aulas 44-45) ────────────────────────────────────────────────────
    (44, "BÔNUS: Planilha de controle alimentar — tutorial completo",
         "Passo a passo de como preencher e usar a planilha de controle incluída no curso.",
         "10min", "video_url"),

    (45, "BÔNUS: Recapitulação e próximos passos",
         "Revisão dos pontos principais e como continuar evoluindo após o curso.",
         "12min", "video_url"),
]

# ── Inserção das aulas ─────────────────────────────────────────────────────────
criadas = 0
existentes = 0

for ordem, titulo, descricao, duracao, tipo in AULAS:
    aula, created = ConteudoDigital.objects.get_or_create(
        produto=produto,
        titulo=titulo,
        defaults={
            "tipo": tipo,
            "ordem": ordem,
            "descricao": descricao,
            "duracao": duracao,
            "url_externa": "",   # preencher com URL do vídeo depois
            "liberado": True,
        },
    )
    if created:
        criadas += 1
        print(f"  [+] Aula {ordem:02d}: {titulo}")
    else:
        existentes += 1

# ── Resumo ─────────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"Produto  : {produto.nome}")
print(f"Slug     : {produto.slug}")
print(f"Preço    : R$ {produto.preco}")
print(f"Status   : {produto.status}")
print(f"Aulas criadas  : {criadas}")
print(f"Já existentes  : {existentes}")
print(f"Total de aulas : {ConteudoDigital.objects.filter(produto=produto).count()}")
print("=" * 60)
print("Pronto! Acesse o admin para adicionar as URLs dos vídeos.")
