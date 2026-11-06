import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import Error as PlaywrightError, sync_playwright

from domain.produto import Produto


class NagumoScraper:

    nome = "Nagumo"

    def __init__(
        self,
        base_url="https://www.nagumo.com.br",
        timeout=30000
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._marcas: dict[str, str | None] = {}

    def buscar(self, termo, categoria):

        print(f"Pesquisando no Nagumo: {termo}")

        with sync_playwright() as playwright:

            browser = playwright.chromium.launch(
                headless=True
            )

            context = browser.new_context(
                locale="pt-BR"
            )

            page = context.new_page()

            try:
                page.goto(
                    self.base_url,
                    wait_until="domcontentloaded",
                    timeout=self.timeout
                )

                # Confere se o site selecionou a loja esperada.
                page.get_by_text(
                    "Loja 026-STO AND2",
                    exact=True
                ).wait_for(timeout=self.timeout)

                # Localiza o campo de pesquisa visível.
                campo = page.locator('input[name="q"]')

                campo.fill(termo)
                campo.press("Enter")

                page.wait_for_url(
                    re.compile(r"/busca(?:\?|$)"),
                    timeout=self.timeout
                )
                page.wait_for_load_state(
                    "domcontentloaded",
                    timeout=self.timeout
                )

                html = page.content()

                soup = BeautifulSoup(
                    html,
                    "html.parser"
                )

                produtos = self._extrair_produtos(
                    soup,
                    categoria,
                    page.request
                )

                if not produtos:
                    print(
                        f"Nenhum produto identificado para: {termo}"
                    )

                return produtos

            finally:
                browser.close()

    def _extrair_produtos(self, soup, categoria, request_context):

        produtos = []
        encontrados = set()

        for elemento in soup.select(".productCard"):

            texto = elemento.get_text(
                " ",
                strip=True
            )

            if not texto or "R$" not in texto:
                continue

            nome = self._extrair_nome(elemento)

            if not nome:
                continue

            preco_elemento = elemento.select_one(".productPrice")
            preco = self._extrair_preco(
                preco_elemento.get_text(" ", strip=True)
                if preco_elemento
                else texto
            )

            if preco is None:
                continue

            link_elemento = elemento.select_one(
                "a[href]"
            )

            link = None

            if link_elemento:
                link = urljoin(
                    self.base_url,
                    link_elemento.get("href")
                )

            chave = (nome.lower(), link)

            if chave in encontrados:
                continue

            encontrados.add(chave)
            marca = self._extrair_marca(link, request_context) if link else None

            if not marca:
                print(f"[AVISO] Marca não identificada para: {nome}")

            produto = Produto(
                nome=nome,
                preco=preco,
                marca=marca,
                categoria=categoria,
                supermercado="Nagumo",
                url=link,
                data_coleta=datetime.now(timezone.utc),
                unidade=self._extrair_unidade(texto),
                disponivel=(
                    False
                    if "produto indisponível" in texto.casefold()
                    else True if "adicionar" in texto.casefold() else None
                )
            )

            produtos.append(produto)

        return produtos

    def _extrair_marca(self, url, request_context):

        if url in self._marcas:
            return self._marcas[url]

        try:
            resposta = request_context.get(
                url,
                timeout=self.timeout
            )
        except PlaywrightError as exc:
            print(f"[AVISO] Não foi possível consultar a marca em {url}: {exc}")
            self._marcas[url] = None
            return None

        if not resposta.ok:
            print(
                f"[AVISO] A página do produto retornou HTTP "
                f"{resposta.status}: {url}"
            )
            self._marcas[url] = None
            return None

        soup = BeautifulSoup(resposta.text(), "html.parser")

        for script in soup.select('script[type="application/ld+json"]'):
            try:
                dados = json.loads(script.string or script.get_text())
            except json.JSONDecodeError:
                continue

            marca = self._marca_em_jsonld(dados)
            if marca:
                self._marcas[url] = marca
                return marca

        self._marcas[url] = None
        return None

    @classmethod
    def _marca_em_jsonld(cls, dados):

        if isinstance(dados, list):
            for item in dados:
                marca = cls._marca_em_jsonld(item)
                if marca:
                    return marca
            return None

        if not isinstance(dados, dict):
            return None

        tipo = dados.get("@type")
        if tipo == "Product" or (
            isinstance(tipo, list) and "Product" in tipo
        ):
            marca = dados.get("brand")
            if isinstance(marca, dict):
                marca = marca.get("name")
            if isinstance(marca, str) and marca.strip():
                return marca.strip()

        return cls._marca_em_jsonld(dados.get("@graph", []))

    @staticmethod
    def _extrair_nome(elemento):

        titulo = elemento.select_one(".productCard__title")
        if titulo:
            nome = titulo.get_text(" ", strip=True)
            if nome:
                return nome

        # Primeira tentativa: cabeçalhos.
        for seletor in ["h2", "h3", "h4"]:

            campo = elemento.select_one(seletor)

            if campo:
                nome = campo.get_text(" ", strip=True)

                if nome:
                    return nome

        # Segunda tentativa: links com nome do produto.
        for link in elemento.select("a[href]"):

            nome = link.get_text(" ", strip=True)

            if (
                nome
                and len(nome) > 5
                and "R$" not in nome
                and "Adicionar" not in nome
            ):
                return nome

        return None

    @staticmethod
    def _extrair_preco(texto):

        # Se houver promoção, prioriza o preço depois de "Por:".
        promocao = re.search(
            r"Por:\s*R\$\s*([\d.]+,\d{2})",
            texto,
            flags=re.IGNORECASE
        )

        if promocao:
            valor = promocao.group(1)

        else:
            resultado = re.search(
                r"R\$\s*([\d.]+,\d{2})",
                texto
            )

            if not resultado:
                return None

            valor = resultado.group(1)

        valor = valor.replace(".", "").replace(",", ".")

        try:
            return Decimal(valor)

        except InvalidOperation:
            return None

    @staticmethod
    def _extrair_unidade(texto):

        resultado = re.search(
            r"Unidade:\s*(.*?)(?=R\$|Adicionar|$)",
            texto,
            flags=re.IGNORECASE
        )

        if resultado:
            return resultado.group(1).strip()

        return None