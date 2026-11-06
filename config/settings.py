import os

COOP_BASE_URL = os.getenv("COOP_BASE_URL", "https://www.coopsupermercado.com.br")
ARQUIVO_JSON = os.getenv("ARQUIVO_JSON", "produtos.json")
TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "20"))

CARREFOUR_BASE_URL = os.getenv("CARREFOUR_BASE_URL", "https://www.carrefour.com.br")
ARQUIVO_JSON1 = os.getenv("ARQUIVO_JSON1", "produtos_Carrefur.json")
HTTP_TIMEOUT1 = int(os.getenv("HTTP_TIMEOUT1", "20"))

NAGUMO_BASE_URL = os.getenv("NAGUMO_BASE_URL", "https://www.nagumo.com.br")
ARQUIVO_JSON2 = os.getenv("ARQUIVO_JSON2", "produtos_Nagumo.json")
# O scraper Nagumo usa Playwright, que recebe timeouts em milissegundos.
HTTP_TIMEOUT2 = int(os.getenv("HTTP_TIMEOUT2", "200")) * 1000




# Consultas iniciais. São termos de pesquisa, não garantias de correspondência exata.
CONSULTAS = [
    ("leite integral", "Leite Integral"),
    ("fralda tamanho P", "Fralda P"),
    ("fralda tamanho M", "Fralda M"),
    ("fralda tamanho G", "Fralda G"),
    ("café", "Café"),
    ("arroz", "Arroz"),
    ("feijão", "Feijão"),
    ("Nescau", "Nescau"),
    ("Achocolatado", "Achocolatado"),
    ("Detergente", "Detergente"),
    ("Amaciante", "Amaciante"),
    ("Shampoo", "Shampoo"),
    ("Papel higiênico", "Papel Higiênico")
]
