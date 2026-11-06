from typing import Protocol
from .produto import Produto

class Scraper(Protocol):
    def buscar(self, termo: str, categoria: str) -> list[Produto]: ...

class ProductRepository(Protocol):
    def salvar(self, produtos: list[Produto]) -> None: ...
