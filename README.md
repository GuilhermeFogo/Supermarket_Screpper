# Coletor de preços - MVP Coop

MVP em Python para consultar o catálogo online da Coop e exportar os resultados para JSON.

## Requisitos
- Python 3.10+
- Acesso à internet

## Instalação

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
python main.py
```

## Observações importantes
- O scraper consulta a rota de catálogo no padrão VTEX. A rota e os campos precisam ser validados no ambiente real da Coop.
- O projeto não usa dados fictícios: se a rota falhar, o erro será informado no terminal e o JSON será salvo com os resultados que tiverem sido coletados.
- O catálogo online não garante preço ou estoque de uma unidade física específica de Santo André.
- Os preços retornados são gravados em `produtos.json` como números.
- As consultas e o limite de resultados podem ser ajustados em `config/settings.py`.
