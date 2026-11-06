from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime

@dataclass(frozen=True)
class Produto:
    nome: str
    preco: Decimal
    marca: str | None
    categoria: str
    supermercado: str
    url: str
    data_coleta: datetime
    unidade: str | None = None
    disponivel: bool = True
