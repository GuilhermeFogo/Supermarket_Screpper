import re

from decimal import Decimal, InvalidOperation
from urllib.parse import quote

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from domain.produto import Produto


class CarrefourScraper:

    nome = "Carrefour"

    def __init__(self, base_url, timeout=30000):

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def buscar(self, termo, categoria):

        produtos = []

        url = (
            f"{self.base_url}/busca/"
            f"{quote(termo)}"
        )

        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=True
            )

            page = browser.new_page(
                locale="pt-BR"
            )

            try:

                print(f"Pesquisando Carrefour: {termo}")

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.timeout
                )

                page.wait_for_timeout(4000)

                # Captura o HTML renderizado pelo navegador.
                html = page.content()

                soup = BeautifulSoup(
                    html,
                    "html.parser"
                )

                produtos = self._extrair_produtos(
                    soup,
                    categoria
                )

            finally:

                browser.close()

        return produtos

    def _extrair_produtos(self, soup, categoria):

        produtos = []

        # Primeira estratégia: localizar elementos de produto.
        # Os seletores serão ajustados conforme o HTML real.
        elementos = soup.select(
            '[data-testid*="product"], '
            'article, '
            '.product-card'
        )

        for elemento in elementos:

            nome_elemento = elemento.select_one(
                '[data-testid*="product-name"], '
                '.product-name, '
                'h2, h3'
            )

            preco_elemento = elemento.select_one(
                '[data-testid*="price"], '
                '.price, '
                '[class*="price"]'
            )

            if not nome_elemento or not preco_elemento:
                continue

            nome = nome_elemento.get_text(
                " ",
                strip=True
            )

            preco = self._converter_preco(
                preco_elemento.get_text(
                    " ",
                    strip=True
                )
            )

            if not nome or preco is None:
                continue

            link_elemento = elemento.select_one("a[href]")

            link = None

            if link_elemento:

                href = link_elemento.get("href")

                if href:
                    link = (
                        href if href.startswith("http")
                        else self.base_url + href
                    )

            produto = Produto(
                nome=nome,
                preco=preco,
                marca=None,
                categoria=categoria,
                supermercado="Carrefour",
                localidade_referencia="Santo André/SP",
                url=link,
                data_coleta=Produto.agora_iso(),
                unidade=None,
                disponivel=None
            )

            produtos.append(produto)

        return produtos

    @staticmethod
    def _converter_preco(texto):

        if not texto:
            return None

        resultado = re.search(
            r'R\$\s*([\d.]+,\d{2})',
            texto
        )

        if not resultado:
            return None

        valor = resultado.group(1)

        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")

        try:
            return Decimal(valor)

        except InvalidOperation:
            return None