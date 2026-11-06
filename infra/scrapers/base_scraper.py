from abc import ABC, abstractmethod
from domain.produto import Produto

class BaseScraper(ABC):
    @abstractmethod
    def buscar(self, termo: str, categoria: str) -> list[Produto]:
        raise NotImplementedError
