from domain.interfaces import Scraper, ProductRepository
from domain.produto import Produto

class ProductService:
    def __init__(self, scrapers: list[Scraper], repository: ProductRepository):
        self.scrapers = scrapers
        self.repository = repository

    def coletar(self, consultas: list[tuple[str, str]]) -> list[Produto]:
        resultados: list[Produto] = []
        for scraper in self.scrapers:
            for termo, categoria in consultas:
                try:
                    encontrados = scraper.buscar(termo, categoria)
                    resultados.extend(encontrados)
                    print(f"[OK] {scraper.__class__.__name__}: {len(encontrados)} resultado(s) para '{termo}'")
                except Exception as exc:
                    # Uma consulta com erro não interrompe as demais.
                    print(f"[ERRO] {scraper.__class__.__name__} / {termo}: {exc}")
        self.repository.salvar(resultados)
        return resultados
