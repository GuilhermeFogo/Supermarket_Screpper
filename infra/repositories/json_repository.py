import json
from pathlib import Path
from domain.produto import Produto

class JsonProductRepository:
    def __init__(self, caminho: str):
        self.caminho = Path(caminho)

    def salvar(self, produtos: list[Produto]) -> None:
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        dados = []
        for p in produtos:
            dados.append({
                "produto": p.nome,
                "preco": float(p.preco),
                "marca": p.marca,
                "categoria": p.categoria,
                "supermercado": p.supermercado,
                "url": p.url,
                "data_coleta": p.data_coleta.isoformat(),
                "disponivel": p.disponivel,
                "unidade": p.unidade,
            })
        self.caminho.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
