from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import quote
import requests

from domain.produto import Produto
from infra.scrapers.base_scraper import BaseScraper

class CoopScraper(BaseScraper):
    """
    Adaptador inicial para o catálogo online Coop.
    A rota de catálogo segue o padrão público de busca VTEX.
    A disponibilidade real da rota e os campos retornados devem ser
    confirmados na primeira execução; não há dados simulados neste scraper.
    """
    def __init__(self, base_url: str, timeout: int = 20):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; PriceResearchMVP/1.0)",
            "Accept": "application/json",
        })

    def buscar(self, termo: str, categoria: str) -> list[Produto]:
        url = (
            f"{self.base_url}/api/catalog_system/pub/products/search/"
            f"{quote(termo)}"
        )
        response = self.session.get(
            url,
            params={"_from": 0, "_to": 49},
            timeout=self.timeout,
        )
        response.raise_for_status()

        try:
            dados = response.json()
        except ValueError as exc:
            raise RuntimeError("A Coop não retornou JSON na rota de catálogo.") from exc

        if not isinstance(dados, list):
            raise RuntimeError("Formato inesperado na resposta do catálogo Coop.")

        produtos: list[Produto] = []
        for item in dados:
            nome = item.get("productName") or item.get("productTitle")
            marca = item.get("brand") or "Não informada"
            link = item.get("link") or item.get("linkText") or ""
            if link and link.startswith("/"):
                link = self.base_url + link

            for variante in item.get("items", []):
                vendedores = variante.get("sellers", [])
                ofertas = [
                    seller.get("commertialOffer", {})
                    for seller in vendedores
                    if seller.get("commertialOffer")
                ]
                oferta = next(
                    (o for o in ofertas if o.get("AvailableQuantity", 0) > 0),
                    ofertas[0] if ofertas else {},
                )
                preco_raw = oferta.get("Price")
                if not nome or preco_raw is None:
                    continue

                try:
                    preco = Decimal(str(preco_raw)).quantize(Decimal("0.01"))
                except (InvalidOperation, ValueError):
                    continue

                disponivel = oferta.get("AvailableQuantity", 0) > 0
                produtos.append(Produto(
                    nome=nome.strip(),
                    preco=preco,
                    marca=str(marca).strip(),
                    categoria=categoria,
                    supermercado="Coop (loja online)",
                    url=link,
                    data_coleta=datetime.now(timezone.utc),
                    disponivel=disponivel,
                ))

        return produtos
